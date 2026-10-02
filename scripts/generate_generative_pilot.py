"""Matched unconditional and motif generation, with all backbones retained."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.backbone import encode_backbone
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.generative import sample_unconditional
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from diagnose_pca_frames import frame
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


from latentfold.fragment_designability import motif_error


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','selection','panel','embedding_cache','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    rows=json.loads(Path(c['selection']).read_text())['rows'];recipe=json.loads(Path(c['protocol']).read_text())
    if len(rows)!=16 or len({r['family'] for r in rows})!=16 or c['samples']!=4 or c['modes']!=recipe['modes']:raise ValueError('Wrong generation scope')
    for h in c['heads']:
        if sha(h['checkpoint'])!=h['checkpoint_sha256'] or recipe['heads'][h['name']]!=h['steps']:raise ValueError('Changed head')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,records=[],controls=[],references=[],batches=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['embedding_cache']) as cache,h5py.File(a.output/'predictions.h5','x') as out:
            encoded={}
            for row in rows:
                ident=row['target_id'];n=row['length'];ref=row['reference'];bb=np.asarray(ref['backbone'],dtype=np.float32)
                if bb.shape!=(n,4,3) or sha(ref['path'])!=ref['sha256']:raise ValueError('Invalid complete experimental backbone')
                basis,degenerate=frame(bb[:,1]);bb=((bb-bb[:,1].mean(0))@basis).astype(np.float32);mask=torch.ones(1,n,dtype=torch.bool,device='cuda')
                z=F.layer_norm(encode_backbone(decoder,torch.from_numpy(bb)[None].cuda(),mask),(8,));encoded[ident]=z
                dn=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='decoder',device='cuda')*decoder.fm.scale_ref
                ca,roundtrip=decoder(z,mask,noise=dn,return_backbone=True);metric=ca_metrics(ca[0].cpu().numpy(),bb[:,1]);g=out.create_group('references/'+ident);g.create_dataset('backbone',data=bb);g.create_dataset('roundtrip',data=roundtrip[0].cpu().numpy());g.create_dataset('latent',data=z[0].cpu().numpy())
                m['references'].append(dict(target_id=ident,pca_near_degenerate=degenerate,**metric))
            for head in c['heads']:
                model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
                for row in rows:
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Generation work cap')
                    ident=row['target_id'];n=row['length'];b=c['samples'];mask=torch.ones(b,n,dtype=torch.bool,device='cuda');esm=torch.zeros(b,n,2560,device='cuda')
                    def noises(stream,index=0,width=8,mult=1):
                        return torch.cat([target_noise([ident],[mult*n],width,seed=c['seed'],sample_index=k,stream=stream+':'+str(index),device='cuda') for k in range(b)])
                    noise=noises('flow');eps=noises('motif');dn=noises('decoder',width=3,mult=4)*decoder.fm.scale_ref
                    zref=encoded[ident].repeat(b,1,1);keep=torch.zeros_like(mask);k=max(8,int(.3*n));st=(n-k)//2;keep[:,st:st+k]=True
                    if ident in c['control_ids']:
                        actual=torch.from_numpy(cache[ident]['80'][:])[None].cuda();generic=sample(model,actual,mask[:1],SampleConfig(steps=head['steps'],guidance=0),noise=noise[:1]);null=sample_unconditional(model,actual,mask[:1],noise=noise[:1],steps=head['steps'])
                        one=decoder(generic,mask[:1],noise=dn[:1]);two=decoder(null,mask[:1],noise=dn[:1]);control=dict(head=head['name'],target_id=ident,latent_max_abs=float((generic-null).abs().max()),**ca_metrics(one[0].cpu().numpy(),two[0].cpu().numpy()));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                        if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Null-only parity control failed')
                    for mode,repaint in c['modes'].items():
                        fixed=None if mode=='unconditional' else (zref,keep)
                        def fresh(i,j):return noises('refinement',i*2+j)
                        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                        z=sample_unconditional(model,esm,mask,noise=noise,steps=head['steps'],fixed=fixed,motif_noise=eps if fixed is not None else None,repaint=repaint,fresh_noise=fresh)
                        _,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        if not np.isfinite(bb).all():raise ValueError('Nonfinite generation')
                        g=out.create_group(f"{head['name']}/{mode}/{ident}");g.create_dataset('backbone',data=bb);g.create_dataset('latent',data=z.cpu().numpy());g.create_dataset('motif_mask',data=keep[0].cpu().numpy())
                        geometry=backbone_geometry(bb);errors=motif_error(bb,out['references/'+ident+'/backbone'][:],keep[0].cpu().numpy())
                        for slot in range(b):m['records'].append(dict(head=head['name'],mode=mode,target_id=ident,family=row['family'],slot=slot,motif_drms=float(errors[slot]),coarse_valid=int(geometry['coarse_valid'][slot])))
                        m['batches'].append(dict(head=head['name'],mode=mode,target_id=ident,length=n,batch=b,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),velocity_evaluations=head['steps']+(head['steps']-1)*(repaint-1)))
                        out.flush();atomic_json(a.output/'manifest.json',m)
                    print('generated',head['name'],ident,flush=True)
                del model;torch.cuda.empty_cache()
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
