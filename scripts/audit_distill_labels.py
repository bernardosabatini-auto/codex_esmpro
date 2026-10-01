"""Decode every teacher latent before committing to longer training runs."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from predict import file_identity
from profile_gpu import Telemetry,atomic_json


@torch.no_grad()
def metrics(bb, reference):
    ca=bb[:,:,1];ref=reference[:,:,1];p=ca-ca.mean(1,keepdim=True);q=ref-ref.mean(1,keepdim=True)
    u,_,v=torch.linalg.svd(p.transpose(1,2)@q);sign=torch.linalg.det(u@v);fix=torch.eye(3,device=bb.device,dtype=bb.dtype).repeat(len(bb),1,1);fix[:,2,2]=sign
    rmsd=((p@(u@fix@v)-q).square().sum(-1).mean(1)).sqrt()
    dp=torch.cdist(ca,ca,compute_mode='donot_use_mm_for_euclid_dist');dr=torch.cdist(ref,ref,compute_mode='donot_use_mm_for_euclid_dist');n=ca.shape[1];idx=torch.arange(n,device=bb.device);eligible=(dr<15)&(idx[:,None]!=idx[None,:]);error=(dp-dr).abs()
    lddt=sum(((error<t)&eligible).sum((1,2)) for t in (.5,1.,2.,4.))/(4*eligible.sum((1,2)))
    peptide=(bb[:,:-1,2]-bb[:,1:,0]).norm(dim=-1);bad=((peptide<1.1)|(peptide>1.6)).float().mean(1);clash=((dp<2.5)&((idx[:,None]-idx[None,:]).abs()>2)).any(2).float().mean(1);gap=((ca[:,1:]-ca[:,:-1]).norm(dim=-1)>4.5).float().mean(1)
    return dict(ca_rmsd=rmsd,ca_lddt=lddt,coarse_valid=(bad<=.05)&(clash<=.01)&(gap<=.01))


def main():
    p=argparse.ArgumentParser()
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,rows=[],controls=[],batches=[]);atomic_json(a.output/'manifest.json',m)
    try:
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True);seen=set();tested=set()
        with torch.no_grad(),inference_precision('fp32'):
            for shard in c['label_shards']:
                path=Path(shard['manifest'])
                if hashlib.sha256(path.read_bytes()).hexdigest()!=shard['manifest_sha256']:raise ValueError('changed label manifest')
                meta=json.loads(path.read_text())
                if meta['status']!='complete':raise ValueError('incomplete labels')
                if file_identity(path.parent/'labels.h5',hash_contents=True)['sha256']!=shard['labels_sha256']:raise ValueError('changed label arrays')
                with h5py.File(path.parent/'labels.h5') as labels:
                    for ident in labels:
                        if ident in seen:raise ValueError('duplicate audit target')
                        seen.add(ident);g=labels[ident];n=g['reference_z'].shape[0];bucket=next(k for k in (128,256,384,512) if n<=k);z=torch.from_numpy(g['teacher_z'][:]).cuda();ref=torch.from_numpy(g['teacher_backbone'][:]).cuda();mask=torch.ones(16,n,device='cuda',dtype=torch.bool)
                        noise=target_noise([ident],[4*n],3,seed=meta['config']['seed'],stream='reconstruction',device='cuda').repeat(16,1,1)*decoder.fm.scale_ref
                        name=f'collect::label_audit::{len(seen)}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:_,bb=decoder(z,mask,noise=noise,return_backbone=True);values={k:v.cpu().numpy() for k,v in metrics(bb,ref).items()};torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        if bucket not in tested:
                            expected=ca_metrics(bb[0,:,1].cpu().numpy(),ref[0,:,1].cpu().numpy());valid=backbone_geometry(bb.cpu().numpy())['coarse_valid'];delta=max(abs(values[k][0]-expected[k]) for k in ('ca_rmsd','ca_lddt'));m['controls'].append(dict(bucket=bucket,max_metric_difference=float(delta),validity_exact=bool(np.array_equal(valid,values['coarse_valid']))));tested.add(bucket)
                            if delta>1e-3 or not np.array_equal(valid,values['coarse_valid']):raise ValueError('GPU audit metrics differ from CPU reference')
                        if not all(np.isfinite(v).all() for v in values.values()):raise ValueError('nonfinite decoded labels')
                        m['rows'].append(dict(id=ident,length=n,mean_ca_lddt=float(values['ca_lddt'].mean()),min_ca_lddt=float(values['ca_lddt'].min()),mean_ca_rmsd=float(values['ca_rmsd'].mean()),input_valid=int(g['coarse_valid'][:].sum()),decoded_valid=int(values['coarse_valid'].sum())))
                        m['batches'].append(dict(nvtx_range=name,seconds=seconds,batch=16,length=n,peak_reserved_bytes=torch.cuda.max_memory_reserved()));atomic_json(a.output/'manifest.json',m)
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('audit work cap')
        if len(seen)!=512 or len(tested)!=4:raise ValueError('incomplete full-corpus audit')
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
