"""Same-device full-panel accuracy and output agreement for compact conditioning."""
import argparse,gc,hashlib,json,time
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
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','protocol','probe_manifest','source_native_manifest','source_native_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    selection=json.loads(Path(c['selection']).read_text());rows=selection['tuning'];protocol=json.loads(Path(c['protocol']).read_text())
    if len(rows)!=64 or len({r['family'] for r in rows})!=64 or [h['name'] for h in c['heads']]!=protocol['heads']:raise ValueError('wrong panel/heads')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,scores=[],controls=[],agreement=[],batches=[],training_updates_executed=0,scope='Full64 tuning panel, original and balanced500; strict FP32 expanded/compact at identical weights and noise. No locked tests or end-to-end speed claims.');atomic_json(a.output/'manifest.json',m)
    try:
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as data,h5py.File(c['source_native_predictions']) as frozen,h5py.File(a.output/'predictions.h5','x') as out:
            for head in c['heads']:
                for key in ('checkpoint','training_manifest'):
                    if head.get(key) and sha(head[key])!=head[key+'_sha256']:raise ValueError('changed '+key)
                model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);guidance=protocol['guidance_by_head'][head['name']];cfg=SampleConfig(steps=25,guidance=guidance)
                for mode in protocol['modes']:
                    controlled=set()
                    for row in rows:
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('compact full-panel work cap')
                        ident=row['id'];n=row['length'];length=row['bucket'];g=cache['tuning'][ident];embedding=g['80'][:]
                        if g.attrs['sequence_sha256']!=row['sequence_sha256'] or hashlib.sha256(embedding.tobytes()).hexdigest()!=c['embedding_arrays_sha256'][ident]:raise ValueError('changed embedding')
                        esm=torch.zeros(3,length,2560,device='cuda');esm[:,:n]=torch.from_numpy(embedding).cuda();mask=torch.arange(length,device='cuda')[None].expand(3,-1)<n;noise=torch.zeros(3,length,8,device='cuda');dn=torch.zeros(3,4*length,3,device='cuda')
                        for k in range(3):
                            noise[k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0]
                            dn[k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                        label=f"collect::compactnative::{head['name']}::{mode}::{ident}";torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(label)
                        try:
                            z=sample(model,esm,mask,cfg,noise=noise,conditioning_ids=[ident]*3,compact_condition=mode=='compact');_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb[:,:n].cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(head=head['name'],mode=mode,target_id=ident,seconds=seconds,nvtx_range=label,peak_reserved_bytes=torch.cuda.max_memory_reserved(),peak_allocated_bytes=torch.cuda.max_memory_allocated()))
                        if length not in controlled:
                            single=sample(model,esm[:1,:n],mask[:1,:n],cfg,noise=noise[:1,:n],conditioning_ids=[ident],compact_condition=mode=='compact');alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:,1],alone);m['controls'].append(dict(head=head['name'],mode=mode,length=length,**control));controlled.add(length)
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('batch control failed')
                        reference=frozen[head['name']][f'cfg{guidance}'][ident][:] if mode=='fp32' else out[head['name']]['fp32'][ident][:]
                        geometry=backbone_geometry(bb);ca=data['train'][ident]['ca_coords'][:]
                        for k,x in enumerate(bb):
                            control=ca_metrics(x[:,1],reference[k,:,1]);m['agreement'].append(dict(head=head['name'],mode=mode,target_id=ident,sample=k,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('source or implementation agreement failed')
                            m['scores'].append(dict(head=head['name'],mode=mode,target_id=ident,sample=k,**ca_metrics(x[:,1],ca),**{key:float(value[k]) for key,value in geometry.items()}))
                        out.require_group(head['name']+'/'+mode).create_dataset(ident,data=bb);out.flush();del esm,mask,noise,dn,z,bb;atomic_json(a.output/'manifest.json',m)
                    print('scored',head['name'],mode,flush=True)
                del model;gc.collect();torch.cuda.empty_cache()
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
