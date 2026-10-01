"""Evaluate preselected layer-60 and final-layer probes on reserved families."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,torch
from torch.nn import functional as F
from latentfold.embedding import FinalESMC
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from profile_gpu import Telemetry,atomic_json
from probe_layers import design


def main():
    p=argparse.ArgumentParser()
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','weights'):
        if hashlib.sha256(Path(c[key]).read_bytes()).hexdigest()!=c[key+'_sha256']:raise ValueError('changed '+key)
    selection=json.loads(Path(c['selection']).read_text());rows=selection['confirmation']
    if len(rows)!=64 or c['layers']!=[60,80] or c['ridge']!=[.001]:raise ValueError('unexpected frozen confirmation arms')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();m=dict(status='running',config=c,scores=[],controls=[],batches=[],scope='Single confirmation comparison on 64 reserved probe families; fixed layer60 versus layer80, ridge0.001 selected previously. These linear probes do not establish a generative-model improvement.');telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True);e=FinalESMC(a.source/'data/esmc6b',precision='fp32');cache={}
        for length in (128,256,384,512):
            group=[r for r in rows if r['bucket']==length]
            for offset in range(0,len(group),8):
                chunk=group[offset:offset+8];values=e([r['sequence'] for r in chunk],length,layers=c['layers'])
                for i,row in enumerate(chunk):cache[row['id']]={k:v[i,:row['length']].cpu() for k,v in values.items()}
        del e,values;torch.cuda.empty_cache();weights=torch.load(c['weights'],map_location='cuda',weights_only=True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
        with h5py.File(selection['dataset']) as source,h5py.File(a.output/'predictions.h5','x') as output,torch.no_grad(),inference_precision('fp32'):
            for layer in c['layers']:
                sg=output.create_group(str(layer))
                for length in (128,256,384,512):
                    group=[r for r in rows if r['bucket']==length];mask=torch.arange(length,device='cuda')[None]<torch.tensor([r['length'] for r in group],device='cuda')[:,None];emb=torch.zeros(len(group),length,2560,device='cuda');noise=torch.zeros(len(group),4*length,3,device='cuda')
                    for i,r in enumerate(group):
                        emb[i,:r['length']]=cache[r['id']][layer].cuda();noise[i,:4*r['length']]=target_noise([r['id']],[4*r['length']],3,seed=c['seed'],stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                    z=F.layer_norm(design(emb)@weights[f'{layer}_0.001'],(8,))*mask[...,None];name=f'collect::confirm::{layer}::{length}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                    try:_,bb=decoder(z,mask,noise=noise,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    m['batches'].append(dict(nvtx_range=name,seconds=seconds,batch=len(group),length=length,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    n=group[0]['length'];single=decoder(z[:1,:n],mask[:1,:n],noise=noise[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],single);m['controls'].append(control)
                    if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('confirmation shape control failed')
                    for i,r in enumerate(group):
                        n=r['length'];ref=source['train'][r['id']]['ca_coords'][:];true_z=torch.from_numpy(source['train'][r['id']]['z'][:]).cuda()
                        m['scores'].append(dict(target_id=r['id'],family=r['family'],layer=layer,ridge=.001,latent_mse=float((z[i,:n]-true_z).square().mean()),**ca_metrics(bb[i,:n,1],ref)));sg.create_dataset(r['id'],data=bb[i,:n])
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
