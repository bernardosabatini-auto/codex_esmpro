"""Matched context-mask contrast and CPU-only physical audit."""
import json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from fragment_junction_core import DRAW_KEYS,flank_bonds
from audit_inpainting_junctions import junctions
from extra_fragment_validation_core import load_conditions
from local_closure_core import score
from latentfold.local_closure import close_backbone
from summarize_compatible_fragment import array_hash
from prepare_overfit import sha
from profile_gpu import atomic_json


def file_stats(c):
    rows=[]
    for p in sorted({r['path'] for r in c['sources']}):
        s=Path(p).stat();rows.append(dict(path=p,size=s.st_size,mtime_ns=s.st_mtime_ns,inode=s.st_ino))
    return rows


def audit_worker(c):
    if file_stats(c)!=c['cpu_verified_file_stats']:raise ValueError('Flank sources changed after CPU verification')
    if c['context_flank']!=8 or c['flank_spec']!=json.loads(Path(c['flank_protocol']).read_text()):raise ValueError('Changed prospective context flank')
    return c['spec']


def audit_sources(c):
    fs=json.loads(Path(c['flank_protocol']).read_text());m=json.loads(Path(c['flank_baseline_manifest']).read_text())
    d=json.loads(Path(c['flank_baseline_report']).read_text());compatible=json.loads(Path(c['flank_compatible_report']).read_text())
    refresh=json.loads(Path(c['flank_refresh_report']).read_text())
    if (fs!=c['flank_spec'] or c['context_flank']!=fs['context_flank'] or c['context_flank']!=8
            or Path(c['flank_baseline_manifest']).parent.name!=fs['baseline']
            or m['status']!='complete' or d['status']!='complete' or d['profile_only'] or d['qualified']
            or not d['junction_weighted'] or not d['numerically_qualified'] or d['manifest_sha256']!=sha(c['flank_baseline_manifest'])
            or d['predictions_sha256']!=sha(c['flank_baseline_predictions'])
            or compatible['status']!='complete' or compatible['next_route']!='global_scaffold_remodeling'
            or refresh['status']!='complete' or not refresh['profile_only'] or not refresh['numerically_qualified']
            or next(r['closed_complete'] for r in refresh['summary'] if r['arm']=='trained' and r['round']==3)!=0
            or any(c[k]!=m['config'][k] for k in ('spec','protocol','selected','training_ids','fragments','decoder_checkpoint',
                    'baseline_manifest','baseline_predictions','diagnostic_manifest','diagnostic_predictions','junction_protocol','junction_spec','junction_loss'))):
        raise ValueError('Unbound context-mask contrast')
    bound={r['path'] for r in c['sources']}
    if any(v not in bound for k,v in c.items() if k.startswith('flank_') and k!='flank_spec'):
        raise ValueError('Unbound flank input')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text());pm=json.loads(Path(c['profile_manifest']).read_text())
        if (not p.get('flank_context') or p['flank_protocol_sha256']!=sha(c['flank_protocol'])
                or pm['config']['context_flank']!=8 or p['manifest_sha256']!=sha(c['profile_manifest'])):
            raise ValueError('Matching wider-mask profile required')


def augment_report(d,run,m):
    c=m['config'];base=json.loads(Path(c['flank_baseline_manifest']).read_text())
    if (base['initial_model_sha256']!=m['initial_model_sha256'] or len(base['training'])<len(m['training'])
            or any(a[k]!=b[k] for a,b in zip(m['training'],base['training']) for k in DRAW_KEYS)):
        raise ValueError('Unmatched junction baseline training draws or initialization')
    if not c['profile_only']:
        profile=json.loads(Path(c['profile_manifest']).read_text())
        if profile['training']!=m['training'][:40] or d['prefix_max_abs']!=0:raise ValueError('Wider-mask profile/full prefix differs')
    ids=sorted({r['target_id'] for r in d['records']});controls={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
    expected={(kind,arm,i) for kind in ('zero_width','nonleak') for arm in ('generated','native') for i in controls}
    if len(m['flank_controls'])!=16 or {(r['kind'],r['arm'],r['target_id']) for r in m['flank_controls']}!=expected:
        raise ValueError('Incomplete wider-mask GPU controls')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train')
    cache_path=run/'flank_closure_manifest.json';cache_file=run/'flank_closed.h5'
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else dict(status='running',predictions_sha256=m['predictions_sha256'],
        code_sha256=sha(c['flank_closure_code']),protocol_sha256=sha(c['flank_closure_protocol']),records={})
    if (cache['predictions_sha256']!=m['predictions_sha256'] or cache['code_sha256']!=sha(c['flank_closure_code'])
            or cache['protocol_sha256']!=sha(c['flank_closure_protocol'])):raise ValueError('Changed flank closure cache inputs')
    if cache['status']=='complete' and cache['closed_sha256']!=sha(cache_file):raise ValueError('Changed completed closure cache')
    closure_spec=json.loads(Path(c['flank_closure_protocol']).read_text());deadline=time.monotonic()+1200;closure_records=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(run/'initial_masked.h5') as initial, \
         h5py.File(c['flank_baseline_predictions']) as old,h5py.File(cache_file,'a') as closed:
        for ident in ids:
            for kind in ('generated','native'):
                parent='parent' if kind=='generated' else 'native_direct';source=old[parent+'/'+ident+'/latent'][:]
                for field in ('latent','backbone'):
                    if not np.array_equal(f[parent+'/'+ident+'/'+field][:],old[parent+'/'+ident+'/'+field][:]):raise ValueError('Original control changed')
                if not np.array_equal(initial[kind+'/'+ident+'/source_latent'][:],source):raise ValueError('Changed unmasked initial source context')
                for suffix in ('cond','null'):
                    if not np.array_equal(f[kind+'_'+suffix+'/'+ident+'/source_latent'][:],source):raise ValueError('Changed unmasked trained source context')
                if ident in controls:
                    for control in ('zero_width','nonleak'):
                        value=initial[kind+'/'+ident+'/zero_width_backbone'][:] if control=='zero_width' else f[kind+'_cond/'+ident+'/nonleak_backbone'][:]
                        expected_bb=old[kind+'_untrained/'+ident+'/backbone'][:] if control=='zero_width' else f[kind+'_cond/'+ident+'/backbone'][:]
                        error=float(np.max(np.abs(value-expected_bb)))
                        logged=next(r for r in m['flank_controls'] if (r['kind'],r['arm'],r['target_id'])==(control,kind,ident))
                        if not np.isfinite(value).all() or error>1e-5 or error!=logged['max_abs']:raise ValueError('Wider-mask numerical control failed')
        for r in d['records']:
            ident=r['target_id'];item=dict(items[ident],id=ident);slot=r['generation_slot'];arm=r['arm'];bb=f[arm+'/'+ident+'/backbone'][slot]
            r['junctions']=junctions(bb,item['start'],20);r['hidden_flank_bonds']=flank_bonds(bb,item['start'],20,8)
            r['connected_raw']=r['raw_gate_passed'] and r['junctions']['valid']
            if arm not in ('generated_cond','generated_untrained'):continue
            parent=f['parent/'+ident+'/backbone'][slot];key=arm+'/'+ident+'/'+str(slot)
            if key in cache['records']:
                repaired=closed[key][:]
                if array_hash(repaired)!=cache['records'][key]['array_sha256']:raise ValueError('Changed cached flank closure')
            else:
                repaired,stats=close_backbone(bb,parent,item['start'],20,closure_spec,deadline=deadline)
                if key in closed:del closed[key]
                closed[key]=repaired;closed.flush();cache['records'][key]=dict(stats,array_sha256=array_hash(repaired));atomic_json(cache_path,cache)
            result=score(repaired,bb,parent,item,arm,slot,r['bucket']);result['hidden_flank_bonds']=flank_bonds(repaired,item['start'],20,8)
            result['refold_eligible_geometry']=result['qualified_raw'] and result['hidden_flank_bonds']['all_edges_valid']
            closure_records.append(result)
    if len(closure_records)!=8*len(ids) or len(cache['records'])!=len(closure_records):raise ValueError('Incomplete wider-mask closure denominator')
    cache.update(status='complete',closed_sha256=sha(cache_file));atomic_json(cache_path,cache)
    for s in d['summary']:
        rr=[r for r in d['records'] if r['arm']==s['arm']]
        s.update(connected_raw=sum(r['connected_raw'] for r in rr),all_hidden_flank_edges_valid=sum(r['hidden_flank_bonds']['all_edges_valid'] for r in rr))
    cs=[]
    for arm in ('generated_cond','generated_untrained'):
        rr=[r for r in closure_records if r['arm']==arm]
        cs.append(dict(arm=arm,samples=len(rr),coarse_valid=sum(r['coarse_valid'] for r in rr),
            complete_geometry=sum(r['qualified_raw'] for r in rr),all_hidden_flank_edges_valid=sum(r['hidden_flank_bonds']['all_edges_valid'] for r in rr),
            refold_eligible_geometry=sum(r['refold_eligible_geometry'] for r in rr)))
    cpu_seconds=sum(r['seconds'] for r in cache['records'].values());cpu_estimate=math.ceil(cpu_seconds*32/len(ids)*1.5+60)
    d.update(flank_context=True,context_flank=8,flank_protocol_sha256=sha(c['flank_protocol']),junction_weighted=True,
        junction_protocol_sha256=sha(c['junction_protocol']),paired_baseline_updates=len(m['training']),flank_controls=m['flank_controls'],
        closure_summary=cs,closure_records=closure_records,closed_sha256=sha(cache_file),cpu_closure_seconds=cpu_seconds,estimated_full_cpu_seconds=cpu_estimate)
    if c['profile_only']:d['qualified']=d['qualified'] and cpu_estimate<=1200
    else:
        count=cs[0]['refold_eligible_geometry'];d['refold_eligibility']=dict(qualified=count>=45,eligible_complete_geometry=count,required=45)
        d['qualified']=count>=45
    d['scope']='Training-only eight-flank context masking with exact20residue coordinate anchors. Same2000training draws as junction-weighted baseline. Untrained wider-mask controls are new; zero-width controls reproduce historical untrained outputs. CPU closure retains original4residue correction window; require every peptide/CAedge in eight hidden flanks valid as well. Only complete128sample endpoint geometry can license matched refolds; geometry is not designability.'
    return d
