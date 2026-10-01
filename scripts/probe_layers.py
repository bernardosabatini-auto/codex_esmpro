"""Matched ridge probes screen layer information using decoded tuning structures."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.embedding import FinalESMC
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from profile_gpu import Telemetry,atomic_json
from predict import file_identity


def design(x):
    x=F.layer_norm(x,(2560,));return torch.cat((x,torch.ones(*x.shape[:-1],1,device=x.device)),dim=-1)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['selection'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['selection_sha256']:raise ValueError('selection changed')
    selection=json.loads(path.read_text());train=selection['train'];tuning=selection['tuning']
    if len(train)!=512 or len(tuning)!=64:raise ValueError('unexpected probe split')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();layers=(20,40,60,80);m=dict(status='running',config=c,batches=[],controls=[],scores=[],scope='512 training families and 64 tuning families. Matched 2561x8 ridge probes with per-token feature normalization and equal protein weighting. Sixty-four probe confirmation families remain unscored. This is a representation screen, not a generative-model comparison.');telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True);e=FinalESMC(a.source/'data/esmc6b',precision='fp32')
        m['embedding_artifacts']=[file_identity(p,hash_contents=True) for p in sorted((a.source/'data/esmc6b').glob('*')) if p.suffix in ('.json','.safetensors')]
        stats={k:torch.zeros(2561,2561,device='cuda',dtype=torch.float64) for k in layers};cross={k:torch.zeros(2561,8,device='cuda',dtype=torch.float64) for k in layers}
        with h5py.File(selection['dataset']) as source,h5py.File(a.output/'embeddings.h5','x') as cache,torch.no_grad(),inference_precision('fp32'):
            for split,rows in (('train',train),('tuning',tuning)):
                cg=cache.create_group(split)
                for length,batch in ((128,32),(256,16),(384,8),(512,8)):
                    group=[r for r in rows if r['bucket']==length]
                    for offset in range(0,len(group),batch):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('probe work cap')
                        chunk=group[offset:offset+batch];name=f'collect::probe_extract::{split}::{length}::{offset}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:
                            embeddings=e([r['sequence'] for r in chunk],length,layers=layers)
                            if split=='train':
                                mask=torch.arange(length,device='cuda')[None]<torch.tensor([r['length'] for r in chunk],device='cuda')[:,None]
                                weights=mask.double()/torch.tensor([r['length'] for r in chunk],device='cuda')[:,None]/512
                                z=torch.zeros(len(chunk),length,8,device='cuda',dtype=torch.float64)
                                for i,r in enumerate(chunk):z[i,:r['length']]=torch.from_numpy(source['train'][r['id']]['z'][:]).cuda()
                                y=z.reshape(-1,8)*weights.reshape(-1,1).sqrt()
                                for layer in layers:
                                    x=design(embeddings[layer]).double().reshape(-1,2561)*weights.reshape(-1,1).sqrt();stats[layer].add_(x.T@x);cross[layer].add_(x.T@y)
                            values={k:v.cpu().numpy() for k,v in embeddings.items()};torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,seconds=seconds,batch=len(chunk),length=length,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        for i,r in enumerate(chunk):
                            g=cg.create_group(r['id']);g.attrs['sequence_sha256']=r['sequence_sha256']
                            for layer,value in values.items():g.create_dataset(str(layer),data=value[i,:r['length']])
                        del embeddings,values
                    atomic_json(a.output/'manifest.json',m);print('layer extraction',split,length,flush=True)
            weights={};identity=torch.eye(2561,device='cuda',dtype=torch.float64);identity[-1,-1]=0
            for layer in layers:
                for ridge in c['ridge']:
                    weights[layer,ridge]=torch.linalg.solve(stats[layer]+ridge*identity,cross[layer]).float()
            torch.save({f'{k[0]}_{k[1]}':v.cpu() for k,v in weights.items()},a.output/'probe_weights.pt')
        del e,stats,cross;torch.cuda.empty_cache()
        ae=a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt';m['decoder_checkpoint']=file_identity(ae,hash_contents=True);decoder=load_proteinae(a.source/'ProteinAE_v1',ae,steps=3).cuda()
        with h5py.File(selection['dataset']) as source,h5py.File(a.output/'embeddings.h5') as cache,h5py.File(a.output/'predictions.h5','x') as output,torch.no_grad(),inference_precision('fp32'):
            for layer in layers:
                for ridge in c['ridge']:
                    setting=f'layer{layer}_ridge{ridge}';sg=output.create_group(setting)
                    for length in (128,256,384,512):
                        rows=[r for r in tuning if r['bucket']==length];mask=torch.arange(length,device='cuda')[None]<torch.tensor([r['length'] for r in rows],device='cuda')[:,None];emb=torch.zeros(len(rows),length,2560,device='cuda');noise=torch.zeros(len(rows),4*length,3,device='cuda')
                        for i,r in enumerate(rows):
                            emb[i,:r['length']]=torch.from_numpy(cache['tuning'][r['id']][str(layer)][:]).cuda();noise[i,:4*r['length']]=target_noise([r['id']],[4*r['length']],3,seed=c['seed'],stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                        z=F.layer_norm(design(emb)@weights[layer,ridge],(8,))*mask[...,None]
                        name=f'collect::probe_decode::{layer}::{ridge}::{length}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:_,bb=decoder(z,mask,noise=noise,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,seconds=seconds,batch=len(rows),length=length,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        if ridge==c['ridge'][0]:
                            n=rows[0]['length'];single=decoder(z[:1,:n],mask[:1,:n],noise=noise[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],single);m['controls'].append(dict(layer=layer,length=length,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('probe decoder batch control failed')
                        for i,r in enumerate(rows):
                            n=r['length'];reference=source['train'][r['id']]['ca_coords'][:];true_z=source['train'][r['id']]['z'][:];pred_z=z[i,:n].cpu().numpy()
                            m['scores'].append(dict(target_id=r['id'],family=r['family'],layer=layer,ridge=ridge,latent_mse=float(np.mean((pred_z-true_z)**2)),**ca_metrics(bb[i,:n,1],reference)))
                            sg.create_dataset(r['id'],data=bb[i,:n])
                    atomic_json(a.output/'manifest.json',m);print('scored',setting,flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
