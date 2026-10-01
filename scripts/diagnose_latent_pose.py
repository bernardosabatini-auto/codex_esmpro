"""Measure latent pose dependence separately from conformational reconstruction."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.backbone import encode_backbone,canonical_backbone_frame
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['native_manifest'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['native_manifest_sha256']:raise ValueError('native manifest changed')
    native=json.loads(path.read_text());rows=[]
    for bucket in (128,256,384,512):
        selected=[r for r in native['records'] if next(k for k in (128,256,384,512) if r['length']<=k)==bucket];selected.sort(key=lambda r:r['id']);rows+=selected[:4]
    if len(rows)!=16:raise ValueError('need sixteen calibration structures')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);m=dict(status='running',config=c,rows=[],batches=[],scope='Sixteen training references; rigid rotations/translations do not create new conformations');atomic_json(a.output/'manifest.json',m);telemetry=None;start=time.monotonic()
    try:
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        gen=torch.Generator().manual_seed(c['seed']);q,_=torch.linalg.qr(torch.randn(8,3,3,generator=gen,dtype=torch.float64));q[:,:,2]*=torch.linalg.det(q)[:,None];q[0]=torch.eye(3);q=q.float().cuda();shift=torch.randn(8,3,generator=gen).cuda()*30;shift[0]=0
        with h5py.File(native['dataset']) as source,torch.no_grad(),inference_precision('fp32'):
            for index,row in enumerate(rows):
                bb=torch.from_numpy(source[row['id']]['backbone'][:]).cuda();n=len(bb);mask=torch.ones(8,n,device='cuda',dtype=torch.bool);rotated=torch.einsum('nai,bij->bnaj',bb,q)+shift[:,None,None,:];fixed=canonical_backbone_frame(rotated)
                noise=target_noise([row['id']],[4*n],3,seed=c['seed'],stream='decoder',device='cuda').repeat(8,1,1)*decoder.fm.scale_ref
                item=dict(target_id=row['id'],length=n,canonical_coordinate_max_difference=float((fixed-fixed[:1]).abs().max()))
                for name,coords in (('raw',rotated),('canonical',fixed)):
                    label=f'collect::pose::{index}::{name}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.nvtx.range_push(label)
                    try:z=encode_backbone(decoder,coords,mask);ca=decoder(z,mask,noise=noise).cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    item[name]=dict(latent_rmse=float((z[1:]-z[:1]).square().mean().sqrt()),reconstruction_rmsd=float(np.mean([ca_metrics(x,bb[:,1].cpu().numpy())['ca_rmsd'] for x in ca])))
                    m['batches'].append(dict(nvtx_range=label,seconds=seconds,length=n,batch=8))
                translated=encode_backbone(decoder,(bb+torch.tensor([40.,-15.,17.],device='cuda'))[None],mask[:1]);base=encode_backbone(decoder,bb[None],mask[:1]);item['translation_latent_max_difference']=float((translated-base).abs().max());m['rows'].append(item);atomic_json(a.output/'manifest.json',m)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=str(error));raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
