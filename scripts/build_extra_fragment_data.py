"""Encode cropped experimental fragments, with no conditioning model loaded."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.decoder import load_proteinae
from latentfold.backbone import encode_backbone
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.fragment_designability import motif_fit
from generate_isolated_motif import canonical_fragment
from extra_fragment_data import audit_config,crop_condition
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());selection=audit_config(c);rows={r['target_id']:r for r in selection['selected']};a.output.mkdir(exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        def encode(bb):
            x=torch.from_numpy(bb)[None].cuda();mask=torch.ones(1,len(bb),dtype=torch.bool,device='cuda');return F.layer_norm(encode_backbone(decoder,x,mask),(8,)),mask
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['backbones']) as src,h5py.File(c['historical_fragments']) as old,h5py.File(a.output/'fragments.h5','x') as out:
            out.create_group('train')
            for ident in c['control_ids']:
                q=old['development/'+ident+'/conditions/f30_center'];z,_=encode(q['fragment'][:]);error=float(np.max(abs(z[0].cpu().numpy()-q['latent'][:])));m['controls'].append(dict(kind='historical',target_id=ident,latent_max_abs=error))
                if error>1e-5:raise ValueError('Historical isolated code changed')
                out.create_dataset('historical/'+ident+'/latent',data=z[0].cpu().numpy())
            for ident in c['target_ids']:
                if time.monotonic()-start>780:raise TimeoutError('Additional encoding cap')
                bb=src[ident+'/backbone'][:];row=rows[ident];st,sequence,fragment,degenerate=crop_condition(bb,row['sequence'],c['spec'].get('fragment_length'));z,mask=encode(fragment);raw=bb[st:st+len(fragment)].astype(np.float64);rot=np.array([[0,-1,0],[1,0,0],[0,0,1]],np.float64);posed,_=canonical_fragment(raw@rot+np.array([11,7,-3],np.float64));zp,_=encode(posed);coord=float(np.max(abs(posed-fragment)));latent=float((zp-z).abs().max());m['controls'].append(dict(kind='pose',target_id=ident,coordinate_max_abs=coord,latent_max_abs=latent))
                if coord>1e-4 or latent>1e-4:raise ValueError('Additional fragment pose control failed')
                noise=target_noise([ident],[4*len(fragment)],3,seed=c['spec']['seed'],stream='fragment_decoder:0',device='cuda')*decoder.fm.scale_ref;_,decoded=decoder(z,mask,noise=noise,return_backbone=True);rt=decoded[0].cpu().numpy();fit=motif_fit(rt,fragment,0)
                g=out.create_group('development/'+ident);g.attrs.update(family=row['family'],length=row['length']);q=g.create_group('conditions/'+c['spec']['condition']);q.attrs.update(start=st,sequence=sequence,near_degenerate=degenerate)
                for key,value in [('fragment',fragment),('latent',z[0].cpu().numpy()),('roundtrip',rt),('pose_fragment',posed),('pose_latent',zp[0].cpu().numpy())]:q.create_dataset(key,data=value)
                out.create_dataset('references/'+ident+'/backbone',data=bb);m['records'].append(dict(target_id=ident,**fit));out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',fragments_sha256=sha(a.output/'fragments.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
