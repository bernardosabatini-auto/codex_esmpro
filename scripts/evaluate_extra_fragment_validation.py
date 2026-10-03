"""One frozen model,64new families,paired noises and132numerical controls."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_cross_attention import load_fragment_adapter
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from fragment_validation_core import raw_rows
from extra_fragment_validation_core import audit_config,load_conditions
from prepare_overfit import sha
from profile_gpu import atomic_json,Telemetry


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec=audit_config(c);a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c,controls=[],batches=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m);telemetry=None
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);telemetry=Telemetry(a.output,True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);net,_=load_legacy(c['checkpoint'],trusted_pickle=True);net.cuda().eval().requires_grad_(False)
        ck=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True);adapter=load_fragment_adapter(ck,net).cuda().eval().requires_grad_(False);del ck
        historical=load_conditions(c['historical_fragments'],c['control_ids']);new=load_conditions(c['fragments'],c['target_ids'],spec.get('condition','f30_center'))
        def sample(ident,item,seed,posed=False,decode=True,drop=False):
            n=item['length'];features=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda();mask=torch.ones(4,n,dtype=torch.bool,device='cuda')
            if posed:coords=(coords.double()@coords.new_tensor([[0,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+coords.new_tensor([11,7,-3],dtype=torch.float64))*keep[...,None]
            noise=torch.cat([target_noise([ident],[n],8,seed=seed,sample_index=k,stream='flow:0',device='cuda') for k in range(4)]);z=sample_fragment(net,adapter,features,keep,mask,noise=noise,steps=50,coordinates=coords,drop_fragment=drop)
            if not decode:return z.cpu().numpy(),None
            dn=torch.cat([target_noise([ident],[4*n],3,seed=seed,sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref;_,bb=decoder(z,mask,noise=dn,return_backbone=True);return z.cpu().numpy(),bb.cpu().numpy()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out,h5py.File(c['historical_predictions']) as old:
            for ident,item in historical.items():
                z,bb=sample(ident,item,spec['historical_seed']);reference=old['development/conditioned/'+ident];rb=reference['backbone'][:];scores=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,rb)];left=raw_rows(bb,item['fragment'],item['start'],c['arm'],ident,item['family']);right=raw_rows(rb,item['fragment'],item['start'],c['arm'],ident,item['family'])
                r=dict(kind='historical',target_id=ident,latent_max_abs=float(np.max(abs(z-reference['latent'][:]))),max_ca_rmsd=max(x['ca_rmsd'] for x in scores),min_ca_lddt=min(x['ca_lddt'] for x in scores),same_decisions=all(x[k]==y[k] for x,y in zip(left,right) for k in ('coarse_valid','raw_gate_passed')));m['controls'].append(r)
                if r['latent_max_abs']>1e-5 or r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99 or not r['same_decisions']:raise ValueError('Historical sampling changed')
                g=out.create_group('historical/'+ident);g.create_dataset('latent',data=z);g.create_dataset('backbone',data=bb)
            for ident,item in new.items():
                if time.monotonic()-tick>spec['work_cap_seconds']:raise TimeoutError('Additional generation cap')
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();start=time.monotonic();z,bb=sample(ident,item,spec['seed'],drop=spec.get('drop_fragment',{}).get(c['arm'],False));torch.cuda.synchronize();seconds=time.monotonic()-start;peak=torch.cuda.max_memory_reserved()/2**30
                if peak>75:raise ValueError('Additional sampling memory cap')
                g=out.create_group('new/'+ident);g.create_dataset('latent',data=z);g.create_dataset('backbone',data=bb)
                for kind,posed in [('same_batch_repeat',False),('pose',True)]:
                    check,_=sample(ident,item,spec['seed'],posed=posed,decode=False,drop=spec.get('drop_fragment',{}).get(c['arm'],False));g.create_dataset(kind,data=check);error=float(np.max(abs(check-z)));m['controls'].append(dict(kind=kind,target_id=ident,latent_max_abs=error))
                    if error>(1e-4 if posed else 1e-5):raise ValueError('Additional sampling repeat/pose failed')
                m['batches'].append(dict(target_id=ident,samples=4,length=item['length'],seconds=seconds,peak_reserved_GiB=peak));out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
