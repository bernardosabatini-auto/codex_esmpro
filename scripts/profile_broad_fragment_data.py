"""Source-to-latent parity and isolated-crop feasibility without teacher generation."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.backbone import encode_backbone,align_backbone_to_reference
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.fragment_designability import motif_fit
from latentfold.ensemble_metrics import backbone_geometry
from generate_isolated_motif import canonical_fragment
from broad_fragment_pilot import audit,qualify
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());rows=audit(c);spec=c['spec'];a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        def encode(bb):
            x=torch.as_tensor(bb,device='cuda')[None];mask=torch.ones(1,len(bb),dtype=torch.bool,device='cuda');return F.layer_norm(encode_backbone(decoder,x,mask),(8,)),mask
        def decode(ident,z,mask,stream):
            n=z.shape[1];noise=target_noise([ident],[4*n],3,seed=spec['seed'],stream=stream,device='cuda')*decoder.fm.scale_ref;_,bb=decoder(z,mask,noise=noise,return_backbone=True);return bb[0].cpu().numpy()
        seen=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['backbones']) as source,h5py.File(c['cache']) as cache,h5py.File(c['historical_fragments']) as old,h5py.File(a.output/'fragments.h5','x') as out:
            for ident in c['control_ids']:
                q=old['development/'+ident+'/conditions/f30_center'];z,_=encode(q['fragment'][:]);error=float(np.max(abs(z[0].cpu().numpy()-q['latent'][:])));m['controls'].append(dict(kind='historical',target_id=ident,latent_max_abs=error));out.create_dataset('historical/'+ident,data=z[0].cpu().numpy())
            for row in rows:
                if time.monotonic()-tick>spec['work_cap_seconds']:raise TimeoutError('Broad data pilot cap')
                ident=row['id'];n=row['length'];raw=torch.from_numpy(source[ident+'/backbone'][:]).cuda();cached=cache['train/'+ident];proxy=raw.clone();proxy[:,1]=torch.from_numpy(cached['ca_coords'][:]).cuda();mask=torch.ones(1,n,device='cuda',dtype=torch.bool);reference=align_backbone_to_reference(raw[None],proxy,mask[0])[0];error=float((reference[:,1]-proxy[:,1]).square().sum(-1).mean().sqrt());encoded=encode_backbone(decoder,reference[None],mask);z=torch.from_numpy(cached['z'][:])[None].cuda();parity=float((z-encoded).square().mean().sqrt());bb=reference.cpu().numpy();decoded=decode(ident,z,mask,'broad_full:0');metric=ca_metrics(decoded[:,1],bb[:,1]);record=dict(target_id=ident,length=n,bucket=row['bucket'],source_ca_error=error,full_encoding_rmse=parity,source_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),decoded_valid=bool(backbone_geometry(decoded[None])['coarse_valid'][0]),decoded_ca_rmsd=metric['ca_rmsd'],fragments=[])
                if error>.02 or parity>.05:raise ValueError('Full source/latent parity failed')
                g=out.create_group('train/'+ident);g.attrs.update(length=n,family=row['family'])
                for key,value in [('reference_backbone',bb),('reference_z',z[0].cpu().numpy()),('encoded_z',encoded[0].cpu().numpy()),('roundtrip',decoded)]:g.create_dataset(key,data=value)
                if row['bucket'] not in seen:
                    again=decode(ident,z,mask,'broad_full:0');m['controls'].append(dict(kind='repeat',target_id=ident,**ca_metrics(again[:,1],decoded[:,1])));g.create_dataset('repeat',data=again);seen.add(row['bucket'])
                for fraction in spec['fractions']:
                    k=max(8,int(fraction*n))
                    for position,start in [('left',0),('center',(n-k)//2),('right',n-k)]:
                        name=f'f{round(fraction*100)}_{position}';crop=bb[start:start+k].astype(np.float64);fragment,degenerate=canonical_fragment(crop);code,cmask=encode(fragment);rt=decode(ident,code,cmask,'broad_fragment:'+name);q=g.create_group('conditions/'+name);q.attrs.update(start=start,sequence=row['sequence'][start:start+k],near_degenerate=degenerate)
                        for key,value in [('fragment',fragment),('latent',code[0].cpu().numpy()),('roundtrip',rt)]:q.create_dataset(key,data=value)
                        record['fragments'].append(dict(condition=name,**motif_fit(rt,fragment,0)))
                        if name=='f30_center':
                            posed,_=canonical_fragment(crop@np.array([[0,-1,0],[1,0,0],[0,0,1]],np.float64)+np.array([11,7,-3],np.float64));pz,_=encode(posed);m['controls'].append(dict(kind='pose',target_id=ident,coordinate_max_abs=float(np.max(abs(posed-fragment))),latent_max_abs=float((pz-code).abs().max())));q.create_dataset('pose_fragment',data=posed);q.create_dataset('pose_latent',data=pz[0].cpu().numpy())
                m['records'].append(record);out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(qualify(m['records'],m['controls'],spec));m.update(status='complete',fragments_sha256=sha(a.output/'fragments.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
        if m['peak_reserved_GiB']>spec['max_reserved_GiB']:raise ValueError('Data pilot memory cap')
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
