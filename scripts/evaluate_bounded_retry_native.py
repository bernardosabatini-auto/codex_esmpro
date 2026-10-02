"""Bounded geometry retries with exact historical first-draw controls."""
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
from antithetic_noise import noise_address,native_scheme,raw_identity_samples


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','protocol','diagnostic','capacity_report','prior_retry_manifest'):
        if c.get(key) and sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());selection=json.loads(Path(c['selection']).read_text());rows=selection['tuning']
    if len(rows)!=64 or len({r['family'] for r in rows})!=64 or [h['name'] for h in c['heads']]!=protocol['heads'] or (protocol['outputs_per_family'],protocol['max_attempts_per_output'])!=(3,4):raise ValueError('Wrong frozen scope')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,draws=[],selections=[],controls=[],batches=[],training_updates_executed=0,scope='Separate geometry-retry pipeline. Historical raw failures retained;64 tuning families only.');atomic_json(a.output/'manifest.json',m)
    try:
        records={}
        with h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as source:
            if set(cache['tuning'])!={r['id'] for r in rows}:raise ValueError('Embedding coverage changed')
            for r in rows:
                g=cache['tuning'][r['id']]
                if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('Embedding sequence changed')
                records[r['id']]=dict(r,esm=torch.from_numpy(g['80'][:]),ca=source['train'][r['id']]['ca_coords'][:])
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            for head in c['heads']:
                scheme=native_scheme(head,protocol)
                for key in ('checkpoint','raw_manifest','training_manifest'):
                    if head.get(key) and sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
                raw=json.loads(Path(head['raw_manifest']).read_text());baseline={(r['target_id'],r['sample']):r for r in raw['scores'] if r['head']==head['raw_head'] and r['guidance']==head['guidance']}
                if len(baseline)!=192:raise ValueError('Incomplete raw comparator')
                model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);torch.manual_seed(c['seed']);cfg=SampleConfig(steps=25,guidance=head['guidance'])
                for length in (128,256,384,512):
                    ids=[r['id'] for r in rows if r['bucket']==length]
                    for offset in range(0,len(ids),8):
                        chunk=ids[offset:offset+8];pending=[(i,k) for i in chunk for k in range(3)];chosen={};attempted={key:0 for key in pending}
                        for attempt in range(4):
                            if not pending:break
                            if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Retry native work cap')
                            batch=len(pending);esm=torch.zeros(batch,length,2560,device='cuda');mask=torch.zeros(batch,length,dtype=torch.bool,device='cuda');noise=torch.zeros(batch,length,8,device='cuda');dn=torch.zeros(batch,4*length,3,device='cuda')
                            for index,(ident,k) in enumerate(pending):
                                r=records[ident];n=r['length'];draw=k+3*attempt;esm[index,:n]=r['esm'].cuda();mask[index,:n]=True
                                latent_index,latent_sign=noise_address(draw,scheme)
                                noise[index,:n]=latent_sign*target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=latent_index,device='cuda')[0]
                                dn[index,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=draw,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                            torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats()
                            z=sample(model,esm,mask,cfg,noise=noise,conditioning_ids=[i for i,k in pending]);_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize()
                            m['batches'].append(dict(head=head['name'],length=length,offset=offset,attempt=attempt,batch=batch,seconds=time.monotonic()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                            if attempt==0 and offset==0:
                                n=records[pending[0][0]]['length'];single=sample(model,esm[:1,:n],mask[:1,:n],cfg,noise=noise[:1,:n]);alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],alone)
                                m['controls'].append(dict(head=head['name'],length=length,**control))
                                if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('Batch control failed')
                            remaining=[]
                            for index,(ident,k) in enumerate(pending):
                                r=records[ident];pred=bb[index,:r['length']];geometry=backbone_geometry(pred[None]);draw=k+3*attempt
                                # Only geometry determines acceptance. Reference scores are audit outputs.
                                accepted=bool(geometry['coarse_valid'][0]);attempted[(ident,k)]+=1
                                if accepted:chosen[(ident,k)]=draw
                                else:remaining.append((ident,k))
                                latent_index,latent_sign=noise_address(draw,scheme)
                                score=dict(head=head['name'],target_id=ident,slot=k,attempt=attempt,draw=draw,latent_noise_index=latent_index,latent_noise_sign=latent_sign,**ca_metrics(pred[:,1],r['ca']),**{key:float(value[0]) for key,value in geometry.items()});m['draws'].append(score)
                                if attempt==0 and k in raw_identity_samples(head,protocol) and any(abs(score[key]-baseline[(ident,k)][key])>1e-6 for key in ('ca_lddt','coarse_valid')):raise ValueError('Historical raw score changed')
                                out.require_group(head['name']+'/'+ident).create_dataset(str(draw),data=pred)
                            pending=remaining;del z,bb,esm,mask,noise,dn
                        for ident in chunk:
                            for k in range(3):m['selections'].append(dict(head=head['name'],target_id=ident,slot=k,selected_draw=chosen.get((ident,k),k),attempts=attempted[(ident,k)],exhausted=(ident,k) not in chosen))
                        out.flush();atomic_json(a.output/'manifest.json',m)
                del model;gc.collect();torch.cuda.empty_cache();print('scored',head['name'],flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
