"""Freeze Gaussian seeds and guided student endpoints, without sample selection."""
import argparse, hashlib, json, time
from pathlib import Path
import h5py, numpy as np, torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig, sample, target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from profile_gpu import Telemetry, atomic_json
from predict import file_identity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    selection_path=Path(c['selection'])
    if hashlib.sha256(selection_path.read_bytes()).hexdigest()!=c['selection_sha256']:raise ValueError('selection changed')
    protocol=Path(c['protocol'])
    if hashlib.sha256(protocol.read_bytes()).hexdigest()!=c['protocol_sha256']:raise ValueError('protocol changed')
    selection=json.loads(selection_path.read_text());rows=selection['train'][c['shard']::4]
    if len(rows)!=128 or c['samples']!=16:raise ValueError('unexpected pair selection')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0)
    torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,records=[],controls=[],batches=[]);atomic_json(a.output/'manifest.json',m)
    try:
        ckpt=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt'
        m['checkpoint']=file_identity(ckpt,hash_contents=True)
        model,_=load_legacy(ckpt,trusted_pickle=True);model.cuda().eval()
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
        telemetry=Telemetry(a.output,True);tested=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['embedding_cache']) as cache,h5py.File(a.output/'pairs.h5','x') as out:
            if set(cache['train'])!={r['id'] for r in selection['train']}:raise ValueError('cache coverage mismatch')
            for index,row in enumerate(sorted(rows,key=lambda r:-r['length'])):
                ident=row['id'];n=row['length'];bucket=row['bucket'];g=cache['train'][ident]
                if g.attrs['sequence_sha256']!=row['sequence_sha256']:raise ValueError('sequence mismatch')
                esm=torch.from_numpy(g['80'][:]).cuda()[None].expand(16,-1,-1)
                mask=torch.ones(16,n,dtype=torch.bool,device='cuda')
                noise=torch.cat([target_noise([ident],[n],8,seed=c['seed'],sample_index=k,device='cuda') for k in range(16)])
                name=f'collect::reflow_pairs::{index}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                try:
                    z=sample(model,esm,mask,SampleConfig(25,2),noise=noise,conditioning_ids=[ident]*16)
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                if bucket not in tested:
                    single=sample(model,esm[:1],mask[:1],SampleConfig(25,2),noise=noise[:1])
                    delta=float((single-z[:1]).square().mean().sqrt())
                    dn=target_noise([ident],[4*n],3,seed=c['seed'],stream='decoder',device='cuda')*decoder.fm.scale_ref
                    ca=decoder(torch.cat((single,z[:1])),mask[:2],noise=dn.repeat(2,1,1)).cpu().numpy()
                    metrics=ca_metrics(ca[0],ca[1]);m['controls'].append(dict(bucket=bucket,latent_rmse=delta,**metrics));tested.add(bucket)
                    if delta>.001 or metrics['ca_lddt']<.99 or metrics['ca_rmsd']>.2:raise ValueError('paired generation batching control failed')
                h=out.create_group(ident);h.attrs['sequence_sha256']=row['sequence_sha256'];h.create_dataset('noise',data=noise.cpu().numpy());h.create_dataset('endpoint',data=z.cpu().numpy());out.flush()
                m['records'].append(dict(id=ident,length=n,bucket=bucket,samples=16))
                m['batches'].append(dict(nvtx_range=name,seconds=seconds,batch=16,length=n,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                atomic_json(a.output/'manifest.json',m);print(index+1,'of 128',flush=True)
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('pair generation cap')
        if tested!={128,256,384,512}:raise ValueError('incomplete controls')
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=repr(error));raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
