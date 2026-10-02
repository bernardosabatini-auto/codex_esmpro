"""Inference-only numerical-solver screen on the frozen64 tuning families."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig,sample,target_noise,sampling_name
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def setting_name(setting):
    return sampling_name(setting)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','protocol','baseline_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed input '+key)
    selection=json.loads(Path(c['selection']).read_text());protocol=json.loads(Path(c['protocol']).read_text());prior=json.loads(Path(c['baseline_manifest']).read_text());rows=selection['tuning']
    if len(rows)!=64 or len({r['family'] for r in rows})!=64 or set(r['id'] for r in rows)&set(r['id'] for r in selection['train']):raise ValueError('invalid tuning split')
    checkpoint=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt'
    if c.get('inference_checkpoint'):
        identity=c['inference_checkpoint'];checkpoint=Path(identity['path'])
        if identity['source_sha256']!=c['checkpoint_sha256'] or not identity['tensor_values_verified'] or sha(checkpoint)!=identity['sha256']:raise ValueError('inference checkpoint changed')
    elif sha(checkpoint)!=c['checkpoint_sha256']:raise ValueError('checkpoint changed')
    if prior['checkpoint']['sha256']!=c['checkpoint_sha256'] or prior['config']['evaluation_seed']!=c['evaluation_seed']:raise ValueError('baseline mismatch')
    baseline={(r['target_id'],r['sample']):r for r in prior['scores'] if r['step']==0 and r['sampling_steps']==25}
    if len(baseline)!=192 or {i for i,k in baseline}!={r['id'] for r in rows}:raise ValueError('prior baseline incomplete')
    previous={}
    if c.get('additional_control_manifest'):
        if sha(c['additional_control_manifest'])!=c['additional_control_manifest_sha256']:raise ValueError('additional solver control changed')
        additional=json.loads(Path(c['additional_control_manifest']).read_text())
        if additional['status']!='complete' or additional['checkpoint_sha256']!=c['checkpoint_sha256'] or additional['config']['selection_sha256']!=c['selection_sha256'] or additional['config']['evaluation_seed']!=c['evaluation_seed']:raise ValueError('incompatible additional control')
        previous={(r['setting'],r['target_id'],r['sample']):r for r in additional['scores']}
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,checkpoint_sha256=c['checkpoint_sha256'],loaded_checkpoint=c.get('inference_checkpoint',dict(path=str(checkpoint),sha256=c['checkpoint_sha256'])),training_updates_executed=0,scores=[],controls=[],batches=[],scope='Original weights,64 tuning families,3 seeds; AFDB predicted references. No independent test scoring.')
    atomic_json(a.output/'manifest.json',m)
    try:
        records={}
        with h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as source:
            if set(cache['tuning'])!={r['id'] for r in rows}:raise ValueError('embedding coverage mismatch')
            for r in rows:
                g=cache['tuning'][r['id']]
                if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('embedding sequence mismatch')
                records[r['id']]=dict(r,esm=torch.from_numpy(g['80'][:]),ca=source['train'][r['id']]['ca_coords'][:])
        model,_=load_legacy(checkpoint,trusted_pickle=True);model.cuda().eval()
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
        torch.manual_seed(c['seed']);telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            for setting in protocol['settings']:
                label=setting_name(setting);config=SampleConfig(**setting);group=out.create_group(label)
                for length in (128,256,384,512):
                    ids=[r['id'] for r in rows if r['bucket']==length]
                    for offset in range(0,len(ids),8):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('solver screen work cap')
                        chunk=ids[offset:offset+8];batch=len(chunk)*3;esm=torch.zeros(batch,length,2560,device='cuda');mask=torch.zeros(batch,length,dtype=torch.bool,device='cuda');noise=torch.zeros(batch,length,8,device='cuda');dn=torch.zeros(batch,4*length,3,device='cuda')
                        for i,ident in enumerate(chunk):
                            r=records[ident];n=r['length'];esm[3*i:3*i+3,:n]=r['esm'].cuda();mask[3*i:3*i+3,:n]=True
                            for k in range(3):
                                noise[3*i+k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0]
                                dn[3*i+k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                        name=f'collect::solver::{label}::{length}::{offset}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                        try:
                            z=sample(model,esm,mask,config,noise=noise,conditioning_ids=[i for i in chunk for _ in range(3)])
                            _,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(setting=label,nvtx_range=name,seconds=seconds,length=length,batch=batch,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        if offset==0:
                            n=records[chunk[0]]['length'];single=sample(model,esm[:1,:n],mask[:1,:n],config,noise=noise[:1,:n]);alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],alone)
                            m['controls'].append(dict(setting=label,length=length,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('solver batch control failed')
                        for i,ident in enumerate(chunk):
                            r=records[ident];pred=bb[3*i:3*i+3,:r['length']];group.create_dataset(ident,data=pred);geometry=backbone_geometry(pred)
                            for k,x in enumerate(pred):
                                score=dict(setting=label,target_id=ident,sample=k,**ca_metrics(x[:,1],r['ca']),**{key:float(value[k]) for key,value in geometry.items()})
                                m['scores'].append(score)
                                prior_score=previous.get((label,ident,k))
                                if prior_score and any(abs(score[key]-prior_score[key])>1e-6 for key in ('ca_lddt','coarse_valid')):raise ValueError('additional solver baseline differs from prior run')
                                if label=='euler_25_cfg2' and any(abs(score[key]-baseline[(ident,k)][key])>1e-6 for key in ('ca_lddt','coarse_valid')):raise ValueError('Euler baseline differs from prior run')
                        del z,bb,esm,mask,noise,dn
                atomic_json(a.output/'manifest.json',m);print('scored',label,flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
