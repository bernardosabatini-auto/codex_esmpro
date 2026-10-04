"""Independent controls, whole-scaffold displacement and unchanged CPU closure."""
import argparse,fcntl,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from context_refresh_core import audit
from extra_fragment_validation_core import load_conditions
from local_closure_core import score
from latentfold.local_closure import close_backbone
from summarize_compatible_fragment import array_hash
from profile_gpu import atomic_json
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];spec,gc,parent=audit(c);b=c['frame_config']['base']
    basic=dict(profile_only=c['profile_only'],manifest_path=str(mp.resolve()),manifest_sha256=sha(mp),protocol_sha256=sha(c['frame_config']['protocol']))
    if m['status']!='complete':return dict(basic,status='failed',qualified=False,error=m.get('error'))
    ids=[r['id'] for r in c['selected']];control_ids={r['id'] for r in c['frame_config']['selected']}
    wanted={(k,a,i) for k in ('desired_replay','repeat','nonleak','pose') for a in spec['models'] for i in control_ids}
    frame=json.loads(Path(c['frame_manifest']).read_text())
    if (len(m['controls'])!=len(wanted) or {(r['kind'],r['arm'],r['target_id']) for r in m['controls']}!=wanted
            or len(m['timing'])!=2*len(ids) or {(r['arm'],r['target_id']) for r in m['timing']}!={(a,i) for a in spec['models'] for i in ids}
            or m['training_updates_executed'] or m['initial_weights']!=m['final_weights']
            or m['initial_weights']['trained']!=parent['evaluated_model_sha256'] or m['initial_weights']['untrained']!=parent['initial_model_sha256']
            or any(m['initial_weights'][k]!=frame['initial_weights'][k] for k in ('encoder','decoder'))
            or m['peak_reserved_GiB']>75 or m['elapsed_seconds']>c['work_cap_seconds'] or m['predictions_sha256']!=sha(run/'predictions.h5')):
        raise ValueError('Incomplete refresh run')
    items=load_conditions(b['fragments'],ids,'c20_center',cohort='train');records=[];controls=[];prefix_error=None
    cache_path=run/'closure_manifest.json';cache_file=run/'closed.h5';source_hash=sha(run/'predictions.h5')
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else dict(status='running',source_predictions_sha256=source_hash,
        closure_code_sha256=sha(b['closure_code']),closure_protocol_sha256=sha(b['closure_protocol']),records={})
    if (cache['source_predictions_sha256']!=source_hash or cache['closure_code_sha256']!=sha(b['closure_code'])
            or cache['closure_protocol_sha256']!=sha(b['closure_protocol'])):raise ValueError('Changed closure cache inputs')
    if cache['status']=='complete' and cache['closed_sha256']!=sha(cache_file):raise ValueError('Changed completed CPU closure')
    deadline=time.monotonic()+1200;closure_spec=json.loads(Path(b['closure_protocol']).read_text())
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['starting_backbones']) as starts,h5py.File(b['source_predictions']) as prior, \
         h5py.File(b['noise_source']) as noises,h5py.File(cache_file,'a') as closed:
        if set(f)!=set(spec['models'])|{'noise'} or any(set(f[k])!=set(ids) for k in f):raise ValueError('Changed refresh denominator')
        for row in c['selected']:
            ident=row['id'];item=dict(items[ident],id=ident);n=row['length'];keep=np.tile(item['keep'].numpy(),(4,1))
            if not np.array_equal(f['noise/'+ident][:],noises['noise/'+ident][:]):raise ValueError('Changed decoder noise')
            reference=prior['parent/'+ident+'/backbone'][:]
            for arm in spec['models']:
                old_arm='generated_cond' if arm=='trained' else 'generated_untrained';g=f[arm+'/'+ident]
                source=starts[old_arm+'/'+ident+'/backbone'][:];expected=source-source.mean((1,2),keepdims=True)
                previous=g['start'][:];anchors=g['anchors'][:]
                if previous.shape!=expected.shape or np.max(np.abs(previous-expected))>1e-4 or not np.array_equal(anchors,np.where(keep[...,None,None],previous,0)):
                    raise ValueError('Changed rigid translation or original requested anchors')
                for key in ('features','coordinates','keep'):
                    expected=np.tile(item[key].numpy()[None],(4,)+(1,)*item[key].ndim)
                    if not np.array_equal(g[key][:],expected):raise ValueError('Changed original isolated fragment input')
                if ident in control_ids:
                    if set(g['controls'])!={'desired_replay','repeat','nonleak','pose'}:raise ValueError('Incomplete refresh control arrays')
                    for kind in g['controls']:
                        expected=prior[old_arm+'/'+ident+'/backbone'][:] if kind=='desired_replay' else g['round1/backbone'][:]
                        value=g['controls/'+kind][:];error=float(np.max(np.abs(value-expected)))
                        logged=next(r for r in m['controls'] if (r['kind'],r['arm'],r['target_id'])==(kind,arm,ident))
                        if not np.isfinite(value).all() or error> (1e-4 if kind=='pose' else 1e-5) or error!=logged['max_abs']:
                            raise ValueError('Independent refresh control failed')
                        controls.append(logged)
                for index in range(1,4):
                    q=g['round'+str(index)];bb=q['backbone'][:];z=q['latent'][:]
                    if (set(q)!={'input','latent','backbone'} or not np.array_equal(q['input'][:],previous) or bb.shape!=(4,n,4,3)
                            or not np.isfinite(bb).all() or np.max(np.abs(bb[keep]-anchors[keep]))>1e-4 or np.max(np.abs(bb.mean((1,2))))>1e-4
                            or z.shape!=(4,n,8) or not np.isfinite(z).all() or np.max(np.abs(z.mean(-1)))>1e-4 or np.max(z.var(-1))>1.0001):
                        raise ValueError('Invalid iteration input/latent/output or changed anchors')
                    previous=bb
                    if index not in spec['reported_rounds']:continue
                    for slot,x in enumerate(bb):
                        key=arm+'/'+ident+'/round'+str(index)+'/'+str(slot)
                        raw=score(x,x,reference[slot],item,arm,slot,row['bucket'])
                        if key in cache['records']:
                            repaired=closed[key][:]
                            if array_hash(repaired)!=cache['records'][key]['array_sha256']:raise ValueError('Changed cached closure output')
                        else:
                            repaired,stats=close_backbone(x,reference[slot],item['start'],20,closure_spec,deadline=deadline)
                            if key in closed:del closed[key]
                            closed[key]=repaired;closed.flush();cache['records'][key]=dict(stats,array_sha256=array_hash(repaired));atomic_json(cache_path,cache)
                        after=score(repaired,x,reference[slot],item,arm,slot,row['bucket'])
                        initial=g['start'][slot];unknown=~keep[slot]
                        shift=np.linalg.norm(x[unknown,1]-initial[unknown,1],axis=-1)
                        records.append(dict(arm=arm,target_id=ident,slot=slot,round=index,bucket=row['bucket'],raw=raw,closed=after,
                                            scaffold_ca_rms_displacement=float(np.sqrt(np.mean(shift**2)))))
        if not c['profile_only']:
            with h5py.File(c['profile_predictions']) as profile:
                differences=[]
                for arm in spec['models']:
                    for ident in control_ids:
                        for index in range(1,4):
                            for key in ('input','latent','backbone'):
                                path=f'{arm}/{ident}/round{index}/{key}';differences.append(float(np.max(np.abs(f[path][:]-profile[path][:]))))
                prefix_error=max(differences)
                if prefix_error!=0:raise ValueError('Profile/full iterative outputs changed')
    if len(records)!=len(ids)*16 or len(cache['records'])!=len(records):raise ValueError('Incomplete closure inventory')
    cache.update(status='complete',closed_sha256=sha(cache_file));atomic_json(cache_path,cache)
    summary=[]
    for arm in spec['models']:
        for index in spec['reported_rounds']:
            rr=[r for r in records if r['arm']==arm and r['round']==index]
            summary.append(dict(arm=arm,round=index,samples=len(rr),raw_coarse=sum(r['raw']['coarse_valid'] for r in rr),
                raw_connected=sum(r['raw']['connected_raw'] for r in rr),raw_complete=sum(r['raw']['qualified_raw'] for r in rr),
                closed_coarse=sum(r['closed']['coarse_valid'] for r in rr),closed_connected=sum(r['closed']['connected_raw'] for r in rr),
                closed_complete=sum(r['closed']['qualified_raw'] for r in rr),mean_scaffold_ca_displacement=float(np.mean([r['scaffold_ca_rms_displacement'] for r in rr]))))
    estimated_gpu=math.ceil(m['elapsed_seconds']*32/len(ids)*1.5+60)
    cpu_seconds=sum(r['seconds'] for r in cache['records'].values());estimated_cpu=math.ceil(cpu_seconds*32/len(ids)*1.5+60)
    qualified=(estimated_gpu<=1080 and estimated_cpu<=1200) if c['profile_only'] else next(r['closed_complete'] for r in summary if r['arm']=='trained' and r['round']==3)>=45
    return dict(basic,status='complete',qualified=qualified,numerically_qualified=True,summary=summary,records=records,controls=len(controls),
        predictions_sha256=source_hash,closed_sha256=sha(cache_file),prefix_max_abs=prefix_error,
        gpu_elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],cpu_closure_seconds=cpu_seconds,
        estimated_full_gpu_seconds=estimated_gpu,estimated_full_cpu_seconds=estimated_cpu,
        scope='Frozen three-pass whole-context refresh on ORIGINAL desired fragments. All training-diagnostic outputs retained. Round1 explanatory only; only round3 can qualify full128x8refolds. Geometry does not establish designability. Costs exclude historical cached starts.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1)
    with (a.runs[0]/'context_refresh_audit.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
        visible={k:v for k,v in d.items() if k!='records'};a.output.with_suffix('.md').write_text('# Whole-scaffold context refresh\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))


if __name__=='__main__':main()
