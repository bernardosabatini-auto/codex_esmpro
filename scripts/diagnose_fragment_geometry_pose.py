"""Separate exact rigid transforms from FP32 coordinate-rounding perturbations."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.fragment_conditioning import sample_fragment
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
    for key in ('parent_manifest','checkpoint','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    parent=json.loads(Path(c['parent_manifest']).read_text())
    if parent['status']!='failed' or parent['updates']!=500 or parent['error']!='ValueError: Geometry conditioner pose dependence':raise ValueError('Wrong diagnostic parent')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],training_updates=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);net,arch=load_legacy(c['checkpoint'],trusted_pickle=True);net.cuda().eval().requires_grad_(False);saved=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True);adapter=FragmentGeometryAdapter(net.d_model,n_layers=len(net.blocks),n_heads=net.n_heads).cuda().eval().requires_grad_(False);adapter.load_state_dict(saved['fragment_adapter']);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);data=load_data(c['fragments'])
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            for ident in c['control_ids']:
                v=data[('development',ident)];q=v['conditions']['f30_center'];n=v['length'];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');features=q['features'][None].expand(4,-1,-1).cuda();keep=q['keep'][None].expand(4,-1).cuda();coordinates=q['coordinates'][None].expand(4,-1,-1).cuda();noise=torch.cat([target_noise([ident],[n],8,seed=2026100211,sample_index=k,stream='flow:0',device='cuda') for k in range(4)]);dn=torch.cat([target_noise([ident],[4*n],3,seed=2026100211,sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                rotation=coordinates.new_tensor([[0,-1,0],[1,0,0],[0,0,1]]);translation=coordinates.new_tensor([11,7,-3]);posed32=(coordinates@rotation+translation)*keep[...,None];posed64=(coordinates.double()@rotation.double()+translation.double())*keep[...,None]
                rng=np.random.default_rng(2026100234);qr=np.linalg.qr(rng.normal(size=(3,3)))[0]
                if np.linalg.det(qr)<0:qr[:,0]*=-1
                arbitrary=(coordinates.double()@torch.from_numpy(qr).cuda()+translation.double())*keep[...,None];variants=[('fp32_original',coordinates,'fp32'),('fp32_rounded_pose',posed32,'fp32'),('fp64_original',coordinates.double(),'fp64'),('fp64_exact_pose',posed64,'fp64'),('fp64_arbitrary_pose',arbitrary,'fp64'),('fp64_rounded_pose',posed32.double(),'fp64')];values={}
                for name,coords,precision in variants:
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Diagnostic cap')
                    adapter.distance_precision=precision;z=sample_fragment(net,adapter,features,keep,mask,noise=noise,coordinates=coords);_,bb=decoder(z,mask,noise=dn,return_backbone=True);values[name]=(z.cpu().numpy(),bb.cpu().numpy());g=out.create_group(ident+'/'+name);g.create_dataset('latent',data=values[name][0]);g.create_dataset('backbone',data=values[name][1])
                for name,base in [('fp32_rounded_pose','fp32_original'),('fp64_original','fp32_original'),('fp64_exact_pose','fp64_original'),('fp64_arbitrary_pose','fp64_original'),('fp64_rounded_pose','fp64_original')]:
                    z,bb=values[name];bz,bbb=values[base];geom=backbone_geometry(bb)['coarse_valid'];bg=backbone_geometry(bbb)['coarse_valid'];scores=[ca_metrics(bb[i,:,1],bbb[i,:,1]) for i in range(4)];m['records'].append(dict(target_id=ident,variant=name,baseline=base,latent_max_abs=float(np.max(abs(z-bz))),max_ca_rmsd=max(r['ca_rmsd'] for r in scores),min_ca_lddt=min(r['ca_lddt'] for r in scores),same_validity=bool(np.array_equal(geom,bg))))
                out.flush();atomic_json(a.output/'manifest.json',m);print('diagnosed',ident,flush=True)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
