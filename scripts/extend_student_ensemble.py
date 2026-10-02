"""Fixed latent-noise128 extension with every old32 sample retained as a control."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','panel','base_manifest','base_predictions','base_scores','teacher_scores','quality_report','embedding_cache','checkpoint','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    recipe=json.loads(Path(c['protocol']).read_text())
    if c['samples']!=128 or c['sample_batch']!=32 or recipe['samples']!=128 or c['name'] not in recipe['pipelines']:raise ValueError('extension scope differs')
    rows={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']}
    if len(c['target_ids'])!=16 or len(set(c['target_ids']))!=16 or not set(c['target_ids'])<=set(rows):raise ValueError('wrong extension targets')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    m=dict(status='running',config=c,targets=[],controls=[],batches=[],scope='Fixed16 development-state families;128 latent draws and fixed decoder noise. Cached-conditioner generation cost excludes ESMC and loading.');start=time.monotonic();telemetry=None
    atomic_json(a.output/'manifest.json',m)
    try:
        model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['embedding_cache']) as cache,h5py.File(c['base_predictions']) as reference,h5py.File(a.output/'predictions.h5','x') as output:
            for ident in c['target_ids']:
                row=rows[ident];n=row['length'];length=next(x for x in (128,256,384,512) if n<=x)
                if cache[ident].attrs['sequence_sha256']!=hashlib.sha256(row['sequence'].encode()).hexdigest():raise ValueError('embedding sequence changed')
                esm=torch.zeros(1,length,2560,device='cuda');esm[0,:n]=torch.from_numpy(cache[ident]['80'][:]).cuda();mask=torch.arange(length,device='cuda')[None]<n
                dn=torch.zeros(32,4*length,3,device='cuda');dn[:,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                chunks=[]
                for offset in range(0,128,32):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('student extension work cap')
                    noise=torch.zeros(32,length,8,device='cuda')
                    for k in range(32):noise[k,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=offset+k,device='cuda')[0]
                    name=f'collect::extension::{ident}::{offset}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                    try:
                        z=sample(model,esm.repeat(32,1,1),mask.repeat(32,1),SampleConfig(steps=25,guidance=c['guidance']),noise=noise,conditioning_ids=[ident]*32,compact_condition=c['compact_condition'])
                        _,bb=decoder(z,mask.repeat(32,1),noise=dn,return_backbone=True);bb=bb[:,:n].cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    if not np.isfinite(bb).all():raise ValueError('nonfinite generated backbone')
                    if offset==0:
                        old=reference[ident][c['setting']]['backbone'][:]
                        if old.shape!=bb.shape:raise ValueError('prefix shape differs')
                        checks=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,old)]
                        valid_equal=np.array_equal(backbone_geometry(bb)['coarse_valid'],backbone_geometry(old)['coarse_valid'])
                        record=dict(target_id=ident,max_ca_rmsd=max(x['ca_rmsd'] for x in checks),min_ca_lddt=min(x['ca_lddt'] for x in checks),validity_identical=bool(valid_equal))
                        m['controls'].append(record)
                        if record['max_ca_rmsd']>.2 or record['min_ca_lddt']<.99 or not valid_equal:raise ValueError('original32 prefix control failed')
                    chunks.append(bb);m['batches'].append(dict(target_id=ident,offset=offset,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),nvtx_range=name));del z,noise
                target=output.create_group(ident);target.create_dataset('backbone',data=np.concatenate(chunks));target.create_dataset('seed_indices',data=np.stack((np.arange(128),np.zeros(128,dtype=int)),axis=1))
                m['targets'].append(ident);output.flush();atomic_json(a.output/'manifest.json',m);print('extended',ident,flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
