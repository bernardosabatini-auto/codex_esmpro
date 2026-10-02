"""Separate64-family accuracy check for every matched teacher head."""
import argparse,gc,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','protocol','baseline_manifest','capacity_report'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    selection=json.loads(Path(c['selection']).read_text());protocol=json.loads(Path(c['protocol']).read_text());rows=selection['tuning']
    if len(rows)!=64 or len({r['family'] for r in rows})!=64 or [h['name'] for h in c['heads']]!=protocol['heads']:raise ValueError('invalid frozen panel/heads')
    prior=json.loads(Path(c['baseline_manifest']).read_text());baseline={(r['target_id'],r['sample']):r for r in prior['scores'] if r['step']==0 and r['sampling_steps']==25}
    if prior['checkpoint']['sha256']!=c['checkpoint_sha256'] or prior['config']['evaluation_seed']!=c['evaluation_seed'] or len(baseline)!=192:raise ValueError('baseline mismatch')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,scores=[],controls=[],batches=[],training_updates_executed=0,scope=f"Separate64 tuning families, AFDB predicted references. Original34 and reserved17 unscored. {c.get('training_family_count',32)}-family training, checkpoint{c.get('training_checkpoint_step',500)}; no training or promotion.")
    atomic_json(a.output/'manifest.json',m)
    try:
        records={}
        with h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as source:
            if set(cache['tuning'])!={r['id'] for r in rows}:raise ValueError('embedding coverage mismatch')
            for r in rows:
                g=cache['tuning'][r['id']]
                if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('embedding sequence mismatch')
                records[r['id']]=dict(r,esm=torch.from_numpy(g['80'][:]),ca=source['train'][r['id']]['ca_coords'][:])
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            for head in c['heads']:
                if sha(head['checkpoint'])!=head['checkpoint_sha256']:raise ValueError('checkpoint changed')
                if head.get('training_manifest') and sha(head['training_manifest'])!=head['training_manifest_sha256']:raise ValueError('checkpoint provenance changed')
                model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);torch.manual_seed(c['seed'])
                for guidance in protocol.get('guidance_by_head',{}).get(head['name'],[1,2]):
                    group=out.require_group(head['name']).create_group(f'cfg{guidance}')
                    for length in (128,256,384,512):
                        ids=[r['id'] for r in rows if r['bucket']==length]
                        for offset in range(0,len(ids),8):
                            if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('accuracy-transfer work cap')
                            chunk=ids[offset:offset+8];batch=len(chunk)*3;esm=torch.zeros(batch,length,2560,device='cuda');mask=torch.zeros(batch,length,dtype=torch.bool,device='cuda');noise=torch.zeros(batch,length,8,device='cuda');dn=torch.zeros(batch,4*length,3,device='cuda')
                            for i,ident in enumerate(chunk):
                                r=records[ident];n=r['length'];esm[3*i:3*i+3,:n]=r['esm'].cuda();mask[3*i:3*i+3,:n]=True
                                for k in range(3):
                                    noise[3*i+k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0]
                                    dn[3*i+k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                            name=f"collect::native::{head['name']}::{guidance}::{length}::{offset}";torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                            try:
                                z=sample(model,esm,mask,SampleConfig(steps=25,guidance=guidance),noise=noise,conditioning_ids=[i for i in chunk for _ in range(3)])
                                _,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                            finally:torch.cuda.nvtx.range_pop()
                            m['batches'].append(dict(head=head['name'],guidance=guidance,nvtx_range=name,seconds=seconds,length=length,batch=batch,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                            if offset==0:
                                n=records[chunk[0]]['length'];single=sample(model,esm[:1,:n],mask[:1,:n],SampleConfig(steps=25,guidance=guidance),noise=noise[:1,:n]);alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],alone)
                                m['controls'].append(dict(head=head['name'],guidance=guidance,length=length,**control))
                                if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('batch control failed')
                            for i,ident in enumerate(chunk):
                                r=records[ident];pred=bb[3*i:3*i+3,:r['length']];group.create_dataset(ident,data=pred);geometry=backbone_geometry(pred)
                                for k,x in enumerate(pred):
                                    score=dict(head=head['name'],guidance=guidance,target_id=ident,sample=k,**ca_metrics(x[:,1],r['ca']),**{key:float(value[k]) for key,value in geometry.items()});m['scores'].append(score)
                                    if head['name']=='original' and guidance==2 and any(abs(score[key]-baseline[(ident,k)][key])>1e-6 for key in ('ca_lddt','coarse_valid')):raise ValueError('original baseline changed')
                            del z,bb,esm,mask,noise,dn
                    atomic_json(a.output/'manifest.json',m);print('scored',head['name'],guidance,flush=True)
                del model;gc.collect();torch.cuda.empty_cache()
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
