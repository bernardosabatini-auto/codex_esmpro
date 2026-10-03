"""Two models, identical new noises, fixed historical batches of four."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from fragment_validation_core import audit_config,raw_rows
from prepare_overfit import sha
from profile_gpu import atomic_json,Telemetry
from train_fragment_conditioning import load_data


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_config(c);spec=c['spec'];a.output.mkdir(exist_ok=False);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],batches=[],training_updates=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);telemetry=Telemetry(a.output,True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();data=load_data(c['fragments'])
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            for arm,source in c['models'].items():
                net,_=load_legacy(source['checkpoint'],trusted_pickle=True);net.cuda().eval().requires_grad_(False)
                ck=torch.load(source['checkpoint'],map_location='cpu',weights_only=False,mmap=True);adapter=FragmentGeometryAdapter(net.d_model,n_layers=len(net.blocks),n_heads=net.n_heads,distance_precision='fp64').cuda().eval().requires_grad_(False);adapter.load_state_dict(ck['fragment_adapter']);del ck
                with h5py.File(source['historical_predictions']) as old:
                    for ident in c['target_ids']:
                        if time.monotonic()-start>spec['generation_work_cap_seconds']:raise TimeoutError('Fresh validation generation cap')
                        v=data['development',ident];q=v['conditions'][spec['condition']];n=v['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');features=q['features'][None].expand(4,-1,-1).cuda();keep=q['keep'][None].expand(4,-1).cuda();coords=q['coordinates'][None].expand(4,-1,-1).cuda()
                        def sample(seed,offset,posed=False,decode=True):
                            noise=torch.cat([target_noise([ident],[n],8,seed=seed,sample_index=k,stream='flow:0',device='cuda') for k in range(offset,offset+4)])
                            cc=coords
                            if posed:
                                cc=coords.double();rot=cc.new_tensor([[0,-1,0],[1,0,0],[0,0,1]]);cc=(cc@rot+cc.new_tensor([11,7,-3]))*keep[...,None]
                            z=sample_fragment(net,adapter,features,keep,mask,noise=noise,steps=50,coordinates=cc)
                            if not decode:return z.cpu().numpy(),None
                            dn=torch.cat([target_noise([ident],[4*n],3,seed=seed,sample_index=k,stream='decoder:0',device='cuda') for k in range(offset,offset+4)])*decoder.fm.scale_ref
                            _,bb=decoder(z,mask,noise=dn,return_backbone=True);return z.cpu().numpy(),bb.cpu().numpy()
                        hz,hb=sample(spec['historical_seed'],0);history=old['development/conditioned/'+ident];expected=history['backbone'][:];scores=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(hb,expected)]
                        start_index=int(torch.where(q['keep'])[0][0]);hr=raw_rows(hb,q['fragment'],start_index,arm,ident,v['family']);er=raw_rows(expected,q['fragment'],start_index,arm,ident,v['family'])
                        control=dict(kind='historical',arm=arm,target_id=ident,latent_max_abs=float(np.max(abs(hz-history['latent'][:]))),max_ca_rmsd=max(x['ca_rmsd'] for x in scores),min_ca_lddt=min(x['ca_lddt'] for x in scores),same_validity=all(x['coarse_valid']==y['coarse_valid'] for x,y in zip(hr,er)),same_strict_decisions=all(x['raw_gate_passed']==y['raw_gate_passed'] for x,y in zip(hr,er)))
                        m['controls'].append(control)
                        if control['latent_max_abs']>1e-5 or control['max_ca_rmsd']>.2 or control['min_ca_lddt']<.99 or not control['same_validity'] or not control['same_strict_decisions']:raise ValueError('Historical control failed')
                        g=out.create_group('historical/'+arm+'/'+ident);g.create_dataset('latent',data=hz);g.create_dataset('backbone',data=hb)
                        samples=16 if ident==spec['focus_id'] else 4;torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();parts=[sample(spec['seed'],offset) for offset in range(0,samples,4)];z,bb=[np.concatenate([x[k] for x in parts]) for k in (0,1)];torch.cuda.synchronize();m['batches'].append(dict(arm=arm,target_id=ident,samples=samples,seconds=time.monotonic()-tick,peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30))
                        g=out.create_group(arm+'/'+ident);g.create_dataset('latent',data=z);g.create_dataset('backbone',data=bb)
                        for kind,posed in [('same_batch_repeat',False),('pose',True)]:
                            check,_=sample(spec['seed'],0,posed=posed,decode=False);g.create_dataset(kind,data=check);error=float(np.max(abs(check-z[:4])));m['controls'].append(dict(kind=kind,arm=arm,target_id=ident,latent_max_abs=error))
                            if error>(1e-5 if kind=='same_batch_repeat' else 1e-4):raise ValueError('Fresh sample control failed')
                        out.flush();atomic_json(a.output/'manifest.json',m);print(arm,ident,samples,flush=True)
                del net,adapter;torch.cuda.empty_cache()
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
