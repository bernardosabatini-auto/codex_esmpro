"""Generate one fixed round from feedback and matched fresh noise."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.backbone import encode_backbone
from latentfold.flow import target_noise
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from fragment_refinement_core import choose_refold
from generate_isolated_motif import canonical_fragment
from prepare_overfit import sha
from profile_gpu import atomic_json
from train_fragment_conditioning import load_data


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','feedback','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--round',type=int,required=True);a=p.parse_args();c=json.loads(a.config.read_text());spec=c['spec']
    feedback=json.loads(a.feedback.read_text())
    if a.round not in spec['rounds'] or set(feedback)!=set(spec['cases']):raise ValueError('Changed round')
    a.output.mkdir(exist_ok=False);start=time.monotonic();m=dict(status='running',round=a.round,config_sha256=sha(a.config),feedback_sha256=sha(a.feedback),controls=[],records=[],entries=[])
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        net,_=load_legacy(c['checkpoint'],trusted_pickle=True);net.cuda().eval().requires_grad_(False)
        ck=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True)
        adapter=FragmentGeometryAdapter(net.d_model,n_layers=len(net.blocks),n_heads=net.n_heads,distance_precision='fp64').cuda().eval().requires_grad_(False)
        adapter.load_state_dict(ck['fragment_adapter']);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval()
        data=load_data(c['fragments']);torch.cuda.reset_peak_memory_stats()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out,h5py.File(c['fragments']) as fragments,h5py.File(c['native_predictions']) as natives:
            for case in c['cases']:
                ident=case['target_id'];n=case['length'];q=data['development',ident]['conditions'][spec['condition']]
                features=q['features'][None].cuda();keep=q['keep'][None].cuda();coords=q['coordinates'][None].cuda();mask=torch.ones(1,n,dtype=torch.bool,device='cuda')
                item=feedback[ident];chosen=choose_refold(item['record']['refolds'])
                with h5py.File(item['refolds']) as f,h5py.File(item['raw']) as raw:
                    reference=f[item['name']+'/'+str(chosen)][:] if chosen is not None else raw[item['dataset']][item['slot']]
                canonical,_=canonical_fragment(reference.astype(np.float64))
                rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=np.float64)
                posed,_=canonical_fragment(reference.astype(np.float64)@rotation+np.array([11,7,-3],np.float64))
                if np.max(abs(canonical-posed))>1e-4:raise ValueError('Whole-refold pose control failed')
                zr=F.layer_norm(encode_backbone(decoder,torch.from_numpy(canonical)[None].cuda(),mask),(8,))
                zp=F.layer_norm(encode_backbone(decoder,torch.from_numpy(posed)[None].cuda(),mask),(8,))
                err=float((zr-zp).abs().max());m['controls'].append(dict(kind='reference_pose',target_id=ident,latent_max_abs=err))
                if err>1e-4:raise ValueError('Encoded reference pose control failed')
                if a.round==2 and ident==spec['cases'][0]:
                    znoise=torch.cat([target_noise([ident],[n],8,seed=2026100211,sample_index=k,stream='flow:0',device='cuda') for k in range(4)])
                    z=sample_fragment(net,adapter,features.expand(4,-1,-1),keep.expand(4,-1),mask.expand(4,-1),noise=znoise,steps=50,coordinates=coords.expand(4,-1,-1))
                    with h5py.File(c['historical_predictions']) as old:expected=old['development/conditioned/'+ident+'/latent'][:]
                    err=float(np.max(abs(z.cpu().numpy()-expected)));m['controls'].append(dict(kind='historical_latent',latent_max_abs=err))
                    if err>1e-5:raise ValueError('Historical sampler changed')
                noise=target_noise([ident],[n],8,seed=spec['seed'],sample_index=a.round-2,stream='flow:0',device='cuda')
                dn=target_noise([ident],[4*n],3,seed=spec['seed'],sample_index=a.round-2,stream='decoder:0',device='cuda')*decoder.fm.scale_ref
                fragment=fragments['development/'+ident+'/conditions/'+spec['condition']+'/fragment'][:]
                out.create_dataset('motifs/'+ident,data=fragment)
                for arm in ('feedback','random','native'):
                    name=f'{arm}_{spec["cases"].index(ident)}';tick=time.monotonic()
                    if arm=='native':bb=natives['references/'+ident+'/backbone'][:]
                    else:
                        z=sample_fragment(net,adapter,features,keep,mask,noise=noise,steps=50,coordinates=coords,reference=zr if arm=='feedback' else None,start_time=spec['start_time'] if arm=='feedback' else 0.)
                        _,x=decoder(z,mask,noise=dn,return_backbone=True);bb=x[0].cpu().numpy()
                        out.create_dataset('latents/'+name,data=z.cpu().numpy())
                    torch.cuda.synchronize();out.create_dataset(name,data=bb[None])
                    m['entries'].append(dict(name=name,head=arm,arm=arm,target_id=ident,family=ident,slot=0,length=n,dataset=name,motif_start=case['motif_start'],fixed_start=case['motif_start'],fixed_sequence=case['fixed_sequence'],repeatability_control=arm=='native'))
                    m['records'].append(dict(name=name,seconds=time.monotonic()-tick,selected_refold=chosen if arm=='feedback' else None,fallback=arm=='feedback' and chosen is None))
                out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
