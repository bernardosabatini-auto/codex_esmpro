"""Generate each latent once; compare decoder integration with matched noise."""
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
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','protocol','source_native_manifest','source_native_predictions','capacity_report'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    prior=json.loads(Path(c['source_native_manifest']).read_text());protocol=json.loads(Path(c['protocol']).read_text());selection=json.loads(Path(c['selection']).read_text());rows=selection['tuning']
    if prior['status']!='complete' or prior['config']['heads']!=c['heads'] or prior['config']['selection_sha256']!=c['selection_sha256'] or prior['config']['evaluation_seed']!=c['evaluation_seed']:raise ValueError('incompatible source native evaluation')
    if len(rows)!=64 or len({r['family'] for r in rows})!=64 or [h['name'] for h in c['heads']]!=protocol['heads'] or protocol['decoder_steps']!=[3,5,10]:raise ValueError('wrong panel or settings')
    baseline={(r['head'],r['guidance'],r['target_id'],r['sample']):r for r in prior['scores']}
    if len(baseline)!=960 or len(prior['scores'])!=960:raise ValueError('incomplete source scores')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    m=dict(status='running',config=c,scores=[],controls=[],reproduction_controls=[],batches=[],training_updates_executed=0,scope='Fixed latent/noise, decoder3/5/10,64 tuning families; component timing only. Locked tests unscored.');start=time.monotonic();telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        records={}
        with h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as source:
            if set(cache['tuning'])!={r['id'] for r in rows}:raise ValueError('embedding coverage changed')
            for r in rows:
                g=cache['tuning'][r['id']]
                if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('embedding sequence changed')
                records[r['id']]=dict(r,esm=torch.from_numpy(g['80'][:]),ca=source['train'][r['id']]['ca_coords'][:])
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out,h5py.File(c['source_native_predictions']) as original:
            for head in c['heads']:
                for field in ('checkpoint','training_manifest'):
                    if head.get(field) and sha(head[field])!=head[field+'_sha256']:raise ValueError('changed '+field)
                model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);torch.manual_seed(c['seed']);guidance=protocol['guidance_by_head'][head['name']][0];cfg=SampleConfig(steps=25,guidance=guidance)
                for length in (128,256,384,512):
                    ids=[r['id'] for r in rows if r['bucket']==length]
                    for offset in range(0,len(ids),8):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('decoder diagnostic work cap')
                        chunk=ids[offset:offset+8];batch=len(chunk)*3;esm=torch.zeros(batch,length,2560,device='cuda');mask=torch.zeros(batch,length,dtype=torch.bool,device='cuda');noise=torch.zeros(batch,length,8,device='cuda');dn=torch.zeros(batch,4*length,3,device='cuda')
                        for i,ident in enumerate(chunk):
                            r=records[ident];n=r['length'];esm[3*i:3*i+3,:n]=r['esm'].cuda();mask[3*i:3*i+3,:n]=True
                            for k in range(3):
                                noise[3*i+k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0]
                                dn[3*i+k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                        name=f"collect::decoderprobe::{head['name']}::{length}::{offset}::flow";torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                        try:z=sample(model,esm,mask,cfg,noise=noise,conditioning_ids=[i for i in chunk for _ in range(3)]);torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(head=head['name'],stage='flow',length=length,offset=offset,nvtx_range=name,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        for i,ident in enumerate(chunk):out.require_group(head['name']+'/latent').create_dataset(ident,data=z[3*i:3*i+3,:records[ident]['length']].cpu().numpy())
                        if offset==0:
                            n=records[chunk[0]]['length'];single=sample(model,esm[:1,:n],mask[:1,:n],cfg,noise=noise[:1,:n])
                        for steps in protocol['decoder_steps']:
                            decoder.n_steps=steps
                            if offset==0:decoder(z,mask,noise=dn,return_backbone=True);torch.cuda.synchronize()
                            name=f"collect::decoderprobe::{head['name']}::{length}::{offset}::decoder{steps}";torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                            try:_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                            finally:torch.cuda.nvtx.range_pop()
                            m['batches'].append(dict(head=head['name'],stage='decoder',decoder_steps=steps,length=length,offset=offset,nvtx_range=name,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                            if offset==0:
                                n=records[chunk[0]]['length'];alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],alone);m['controls'].append(dict(head=head['name'],decoder_steps=steps,length=length,**control))
                                if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('decoder batch control failed')
                            for i,ident in enumerate(chunk):
                                r=records[ident];pred=bb[3*i:3*i+3,:r['length']];out.require_group(head['name']+f'/decoder{steps}').create_dataset(ident,data=pred);geometry=backbone_geometry(pred)
                                for k,x in enumerate(pred):
                                    score=dict(head=head['name'],guidance=guidance,decoder_steps=steps,target_id=ident,sample=k,**ca_metrics(x[:,1],r['ca']),**{key:float(value[k]) for key,value in geometry.items()});m['scores'].append(score)
                                    if steps==3:
                                        reference=baseline[head['name'],guidance,ident,k]
                                        if any(abs(score[key]-reference[key])>1e-6 for key in ('ca_lddt','coarse_valid')):raise ValueError('source decoder3 scores changed')
                                        control=ca_metrics(x[:,1],original[head['name']][f'cfg{guidance}'][ident][k,:,1]);m['reproduction_controls'].append(dict(head=head['name'],target_id=ident,sample=k,**control))
                                        if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('source decoder3 backbone changed')
                            atomic_json(a.output/'manifest.json',m)
                        del z,bb,esm,mask,noise,dn
                del model;gc.collect();torch.cuda.empty_cache();print('decoded',head['name'],flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
