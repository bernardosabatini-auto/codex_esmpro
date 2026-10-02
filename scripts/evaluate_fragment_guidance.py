"""Fixed guidance1/2screen, retaining every raw sample and matched controls."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_designability import motif_fit
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from train_fragment_conditioning import load_data
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('generation_manifest','training_report','checkpoint','fragments','parent_predictions','decoder_checkpoint','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if c['guidance']!=[1,2] or c['samples']!=4 or c['steps']!=50:raise ValueError('Changed fixed sampling recipe')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],batches=[],training_updates=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);model,_=load_legacy(c['checkpoint'],trusted_pickle=True);model.cuda().eval().requires_grad_(False);checkpoint=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True);adapter=FragmentGeometryAdapter(model.d_model,n_layers=len(model.blocks),n_heads=model.n_heads,distance_precision='fp64').cuda().eval().requires_grad_(False);adapter.load_state_dict(checkpoint['fragment_adapter']);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();data=load_data(c['fragments'],checkpoint['experiment'].get('fragment_representation','latent_geometry'))
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['parent_predictions']) as parent,h5py.File(a.output/'predictions.h5','x') as out:
            for index,(cohort,ident) in enumerate(sorted(k for k in data if k[0]=='development')):
                v=data[(cohort,ident)];q=v['conditions']['f30_center'];n=v['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');features=q['features'][None].expand(4,-1,-1).cuda();keep=q['keep'][None].expand(4,-1).cuda();coords=q['coordinates'][None].expand(4,-1,-1).cuda();st=int(torch.where(keep[0])[0][0]);noise=torch.cat([target_noise([ident],[n],8,seed=c['seed'],sample_index=k,stream='flow:0',device='cuda') for k in range(4)]);dn=torch.cat([target_noise([ident],[4*n],3,seed=c['seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                for guidance in (c['guidance'] if index%2==0 else c['guidance'][::-1]):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Guidance screen cap')
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();z=sample_fragment(model,adapter,features,keep,mask,noise=noise,steps=50,coordinates=coords,guidance=guidance);_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick;g=out.create_group(f'guidance{guidance}/{ident}');g.create_dataset('backbone',data=bb);g.create_dataset('latent',data=z.cpu().numpy());valid=backbone_geometry(bb)['coarse_valid']
                    for slot in range(4):m['records'].append(dict(guidance=guidance,target_id=ident,family=v['family'],slot=slot,coarse_valid=bool(valid[slot]),**motif_fit(bb[slot],q['fragment'],st)))
                    m['batches'].append(dict(guidance=guidance,target_id=ident,seconds=seconds,peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30,velocity_evaluations=50*guidance))
                    if guidance==1:
                        old=parent['development/conditioned/'+ident];expected=old['backbone'][:];dz=float(np.max(abs(z.cpu().numpy()-old['latent'][:])))
                        scores=[ca_metrics(bb[k,:,1],expected[k,:,1]) for k in range(4)];control=dict(kind='historical_conditioned',target_id=ident,latent_max_abs=dz,max_ca_rmsd=max(r['ca_rmsd'] for r in scores),min_ca_lddt=min(r['ca_lddt'] for r in scores),same_validity=bool(np.array_equal(valid,backbone_geometry(expected)['coarse_valid'])));m['controls'].append(control)
                        if dz>1e-5 or control['max_ca_rmsd']>.2 or control['min_ca_lddt']<.99 or not control['same_validity']:raise ValueError('Historical conditioned control failed')
                    elif ident in c['control_ids']:
                        cc=coords.double();rotation=cc.new_tensor([[0,-1,0],[1,0,0],[0,0,1]]);posed=(cc@rotation+cc.new_tensor([11,7,-3]))*keep[...,None];check=sample_fragment(model,adapter,features,keep,mask,noise=noise,steps=50,coordinates=posed,guidance=2);err=float((check-z).abs().max());m['controls'].append(dict(kind='guided_pose',target_id=ident,latent_max_abs=err))
                        if err>1e-4:raise ValueError('Guided pose control failed')
                if ident in c['control_ids']:
                    z=sample_fragment(model,adapter,features,keep,mask,noise=noise,steps=50,coordinates=coords,guidance=0);old=parent['development/null/'+ident+'/latent'][:];err=float(np.max(abs(z.cpu().numpy()-old)));m['controls'].append(dict(kind='historical_null',target_id=ident,latent_max_abs=err))
                    if err>1e-5:raise ValueError('Guidance-zero control failed')
                out.flush();atomic_json(a.output/'manifest.json',m);print('guided',ident,flush=True)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
