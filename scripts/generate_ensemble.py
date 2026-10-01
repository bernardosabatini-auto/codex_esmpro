"""Separate latent and decoder diversity on a frozen development panel."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.conditioning import ResidualConditioner
from latentfold.decoder import load_proteinae
from latentfold.embedding import FinalESMC
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from predict import file_identity
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['panel'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['panel_sha256']:raise ValueError('changed panel')
    rows=json.loads(path.read_text())['development']
    if len(rows)!=48 or len({r['family'] for r in rows})!=48:raise ValueError('expected 48 distinct development families')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();m=dict(status='running',config=c,batches=[],controls=[],targets=[],precision='strict FP32',timing_scope='Separate conditioner extraction, latent generation and decoder batches; includes transfers, excludes model loading and HDF5 writes');telemetry=None
    atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True)
        if c.get('embedding_cache'):
            path=Path(c['embedding_cache']).resolve();identity=file_identity(path,hash_contents=True)
            if identity['sha256']!=c['embedding_cache_sha256']:raise ValueError('changed ensemble embedding cache')
            with h5py.File(path) as cached:
                if set(cached)!={r['query_id'] for r in rows}:raise ValueError('ensemble cache target coverage mismatch')
                for row in rows:
                    g=cached[row['query_id']]
                    if g.attrs['sequence_sha256']!=hashlib.sha256(row['sequence'].encode()).hexdigest() or g['80'].shape!=(row['length'],2560):raise ValueError('cached sequence/shape mismatch')
            (a.output/'embeddings.h5').symlink_to(path);m['embedding_cache']=identity
            m['timing_scope']='Cached-conditioner ensemble generation; excludes ESMC extraction. Not end-to-end sequence timing.'
        else:
            e=FinalESMC(a.source/'data/esmc6b',precision='fp32')
            m['embedding_artifacts']=[file_identity(p,hash_contents=True) for p in sorted((a.source/'data/esmc6b').glob('*')) if p.suffix in ('.json','.safetensors')]
            with h5py.File(a.output/'embeddings.h5','x') as cache:
                for length,batch in ((128,32),(256,16),(384,8),(512,8)):
                    group=[r for r in rows if next(x for x in (128,256,384,512) if r['length']<=x)==length]
                    for offset in range(0,len(group),batch):
                        chunk=group[offset:offset+batch];name=f'collect::embedding::{length}::{offset}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:
                            values={k:v.cpu().numpy() for k,v in e([r['sequence'] for r in chunk],length,layers=(20,40,60,80)).items()};torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,stage='embedding',seconds=seconds,length=length,batch=len(chunk),peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        for i,row in enumerate(chunk):
                            g=cache.create_group(row['query_id']);g.attrs['sequence_sha256']=hashlib.sha256(row['sequence'].encode()).hexdigest()
                            for layer,value in values.items():g.create_dataset(str(layer),data=value[i,:row['length']])
            del e;torch.cuda.empty_cache()
        ckpt=Path(c['checkpoint']) if c.get('checkpoint') else a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt';ae=a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt'
        m['checkpoint']=file_identity(ckpt,hash_contents=True);m['decoder_checkpoint']=file_identity(ae,hash_contents=True)
        if c.get('checkpoint') and m['checkpoint']['sha256']!=c['checkpoint_sha256']:raise ValueError('changed trained checkpoint')
        model,_=load_legacy(ckpt,trusted_pickle=True);model.cuda().eval().requires_grad_(False)
        conditioner=None
        if c.get('conditioner'):
            adapter=c['conditioner'];identity=file_identity(Path(adapter['checkpoint']),hash_contents=True)
            if identity['sha256']!=adapter['sha256']:raise ValueError('changed conditioner weights')
            conditioner=ResidualConditioner(adapter['arm'],width=adapter['width'],bound=adapter['bound']).cuda().eval().requires_grad_(False)
            conditioner.load_state_dict(torch.load(adapter['checkpoint'],map_location='cuda',weights_only=True),strict=True);m['conditioner']=identity
        decoder=load_proteinae(a.source/'ProteinAE_v1',ae,steps=3).cuda().eval()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'embeddings.h5') as cache,h5py.File(a.output/'predictions.h5','x') as output:
            for index,row in enumerate(rows):
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('experiment work cap')
                ident=row['query_id'];n=row['length'];length=next(x for x in (128,256,384,512) if n<=x)
                esm=torch.zeros(1,length,2560,device='cuda');esm[:,:n]=torch.from_numpy(cache[ident]['80'][:]).cuda();mask=torch.arange(length,device='cuda')[None]<n
                if conditioner is not None:
                    layers={80:esm}
                    for layer in (20,40,60):
                        layers[layer]=torch.zeros_like(esm);layers[layer][:,:n]=torch.from_numpy(cache[ident][str(layer)][:]).cuda()
                    esm=conditioner(layers,mask)
                noise=torch.zeros(32,length,8,device='cuda');dn=torch.zeros(32,4*length,3,device='cuda')
                for k in range(32):
                    noise[k,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=k,device='cuda')[0]
                    dn[k,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                target=output.create_group(ident);target.attrs['family']=row['family'];target.attrs['sequence_sha256']=hashlib.sha256(row['sequence'].encode()).hexdigest()
                for guidance in ([2,1] if ident in c['guidance_controls'] else [2]):
                    cfg=SampleConfig(steps=25,guidance=guidance);g=target.create_group(f'cfg{guidance}')
                    name=f'collect::latent::{index}::{guidance}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                    try:
                        z=sample(model,esm.repeat(32,1,1),mask.repeat(32,1),cfg,noise=noise,conditioning_ids=[ident]*32);torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    m['batches'].append(dict(nvtx_range=name,stage='latent',seconds=seconds,length=length,batch=32,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    # Control unpadded single inference without cross-sample reuse.
                    single=sample(model,esm[:,:n],mask[:,:n],cfg,noise=noise[:1,:n])
                    expected=decoder(single,mask[:,:n],noise=dn[:1,:4*n])[0].cpu().numpy()
                    g.create_dataset('z',data=z[:,:n].cpu().numpy())
                    arms={'latent':[(k,0) for k in range(32)],'decoder':[(0,k) for k in range(32)],'factorial':[(i,j) for i in range(8) for j in range(4)]}
                    for arm,pairs in arms.items():
                        zi=torch.tensor([i for i,j in pairs],device='cuda');di=torch.tensor([j for i,j in pairs],device='cuda')
                        name=f'collect::decoder::{index}::{guidance}::{arm}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:
                            _,bb=decoder(z[zi],mask.repeat(32,1),noise=dn[di],return_backbone=True);bb=bb[:,:n].cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        if not np.isfinite(bb).all():raise ValueError('nonfinite prediction')
                        if arm=='latent':
                            control=ca_metrics(bb[0,:,1],expected);m['controls'].append(dict(target_id=ident,guidance=guidance,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('production batch/reuse control failed')
                        ag=g.create_group(arm);ag.create_dataset('backbone',data=bb);ag.create_dataset('seed_indices',data=pairs)
                        m['batches'].append(dict(nvtx_range=name,stage='decoder',seconds=seconds,length=length,batch=32,arm=arm,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                m['targets'].append(dict(id=ident,length=n,category=row['category']));output.flush();atomic_json(a.output/'manifest.json',m);print('ensemble',index+1,'of',len(rows),flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
