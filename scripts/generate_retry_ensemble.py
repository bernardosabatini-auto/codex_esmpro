"""External latent ensembles with bounded geometry-only retries and raw evidence."""
import argparse,hashlib,json,time
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
    for key in ('protocol','panel','native_manifest','capacity_report','embedding_cache','decoder_checkpoint','checkpoint','training_manifest','parent_manifest','parent_predictions','parent_scores'):
        if c.get(key) and sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    recipe=json.loads(Path(c['protocol']).read_text());rows=json.loads(Path(c['panel']).read_text())['development']
    if c['name'] not in recipe['heads'] or (c['samples'],c['max_attempts'])!=(32,4) or c['noise_arms']!=['raw','latent'] or len(rows)!=48 or len({r['family'] for r in rows})!=48:raise ValueError('Wrong frozen scope')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,targets=[],controls=[],parent_controls=[],batches=[],draws=[],selections=[],training_updates_executed=0,timing_scope='Cached-conditioner generation only, excludes model loading, controls, geometry checks and disk I/O. Retry generation costs retained.');atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True);model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();cfg=SampleConfig(steps=25,guidance=c['primary_guidance'])
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['embedding_cache']) as cache,h5py.File(a.output/'predictions.h5','x') as out:
            if set(cache)!={r['query_id'] for r in rows}:raise ValueError('Embedding coverage changed')
            for row in rows:
                ident=row['query_id'];n=row['length'];length=next(x for x in (128,256,384,512) if n<=x);cached=cache[ident]
                if cached.attrs['sequence_sha256']!=hashlib.sha256(row['sequence'].encode()).hexdigest() or cached['80'].shape!=(n,2560):raise ValueError('Embedding sequence/shape mismatch')
                esm=torch.zeros(1,length,2560,device='cuda');esm[:,:n]=torch.from_numpy(cached['80'][:]).cuda();mask=torch.arange(length,device='cuda')[None]<n
                dn=torch.zeros(1,4*length,3,device='cuda');dn[0,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                group=out.create_group(ident).create_group(f"cfg{c['primary_guidance']}");attempt_group=group.create_group('attempts');pending=list(range(32));selected_indices=np.arange(32);used=np.zeros(32,dtype=int);all_indices=[];all_bb=[];raw=None;selected=None
                for attempt in range(4):
                    if not pending:break
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('External retry work cap')
                    b=len(pending);noise=torch.zeros(b,length,8,device='cuda')
                    for index,k in enumerate(pending):noise[index,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=k+32*attempt,device='cuda')[0]
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                    z=sample(model,esm.repeat(b,1,1),mask.repeat(b,1),cfg,noise=noise,conditioning_ids=[ident]*b,compact_condition=c['compact_condition']);_,bb=decoder(z,mask.repeat(b,1),noise=dn.repeat(b,1,1),return_backbone=True);bb=bb[:,:n].cpu().numpy();torch.cuda.synchronize()
                    m['batches'].append(dict(target_id=ident,attempt=attempt,batch=b,seconds=time.monotonic()-tick,length=length,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    if not np.isfinite(bb).all():raise ValueError('Nonfinite generated backbone')
                    valid=backbone_geometry(bb)['coarse_valid']
                    if attempt==0:
                        raw=bb.copy();selected=raw.copy()
                        single=sample(model,esm[:,:n],mask[:,:n],cfg,noise=noise[:1,:n],conditioning_ids=[ident],compact_condition=c['compact_condition']);alone=decoder(single,mask[:,:n],noise=dn[:,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:,1],alone)
                        m['controls'].append(dict(target_id=ident,**control))
                        if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('Batching control failed')
                        if c.get('parent_predictions'):
                            with h5py.File(c['parent_predictions']) as parent:old=parent[ident][f"cfg{c['primary_guidance']}"]['latent']['backbone'][:]
                            if old.shape!=raw.shape:raise ValueError('Raw parent shape changed')
                            old_valid=backbone_geometry(old)['coarse_valid'];checks=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(raw,old)];parent_control=dict(target_id=ident,max_ca_rmsd=max(r['ca_rmsd'] for r in checks),min_ca_lddt=min(r['ca_lddt'] for r in checks),validity_identical=bool(np.array_equal(valid,old_valid)));m['parent_controls'].append(parent_control)
                            if parent_control['max_ca_rmsd']>.2 or parent_control['min_ca_lddt']<.99 or not parent_control['validity_identical']:raise ValueError('Historical raw ensemble control failed')
                    remaining=[]
                    for index,k in enumerate(pending):
                        draw=k+32*attempt;used[k]+=1;all_indices.append(draw);all_bb.append(bb[index]);m['draws'].append(dict(target_id=ident,slot=k,attempt=attempt,draw=draw,coarse_valid=int(valid[index])))
                        if valid[index]:selected[k]=bb[index];selected_indices[k]=draw
                        else:remaining.append(k)
                    pending=remaining;del noise,z,bb
                for k in range(32):m['selections'].append(dict(target_id=ident,slot=k,attempts=int(used[k]),selected_draw=int(selected_indices[k]),exhausted=k in pending))
                for mode,backbone,indices in [('raw',raw,np.arange(32)),('latent',selected,selected_indices)]:
                    g=group.create_group(mode);g.create_dataset('backbone',data=backbone);g.create_dataset('seed_indices',data=np.stack([indices,np.zeros(32,dtype=int)],axis=1))
                attempt_group.create_dataset('backbone',data=np.stack(all_bb));attempt_group.create_dataset('draw_indices',data=all_indices)
                m['targets'].append(dict(id=ident,length=n,category=row['category']));out.flush();atomic_json(a.output/'manifest.json',m);print('scored',len(m['targets']),'of48',flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
