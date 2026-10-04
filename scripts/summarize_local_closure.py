"""Independent CPU fixed-atom, topology, physical-gate and prefix audit."""
import argparse
import json
import math
from pathlib import Path
import h5py
import numpy as np
from local_closure_core import audit,score,ROTATION,OFFSET
from latentfold.local_closure import geometry_audit,topology
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];spec=audit(c)
    if m['status']!='complete':return dict(status='failed',profile_only=c['profile_only'],qualified=False,error=m.get('error'),manifest_path=str(mp.resolve()),manifest_sha256=sha(mp))
    ids=[r['id'] for r in c['selected']];arms=spec['execution']['arms'];wanted={(a,i,k) for a in arms for i in ids for k in range(4)}
    if (len(m['records'])!=len(wanted) or {(r['arm'],r['target_id'],r['slot']) for r in m['records']}!=wanted
            or len(m['controls'])!=20 or m['gpus_used']!=0 or m['predictions_sha256']!=sha(run/'predictions.h5')
            or any(not math.isfinite(r[k]) or r[k]<0 for r in m['records'] for k in ('initial_loss','final_loss','seconds'))
            or any(r['iterations']>spec['solver']['max_iter'] for r in m['records'])):
        raise ValueError('Incomplete closure run')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');records=[]
    with h5py.File(c['source_predictions']) as src,h5py.File(run/'predictions.h5') as out:
        if set(out)!=set(arms)|{'controls','pose'} or any(set(out[a])!=set(ids) for a in arms):raise ValueError('Changed output inventory')
        for ident in c['profile_ids']:
            item=items[ident];parent=src['parent/'+ident+'/backbone'][0]
            for kind in ('noop','perturbation'):
                g=out['controls/'+kind+'/'+ident];source=g['source'][:];bb=g['backbone'][:]
                expected=parent.copy();residues=topology(len(parent),item['start'],20,4)['residues']
                if kind=='perturbation':expected[residues]+=.05*np.random.default_rng(2026100461).normal(size=(len(residues),4,3))
                fixed=np.ones(len(parent),bool);fixed[residues]=False
                if (not np.array_equal(source,expected) or not np.array_equal(bb[fixed],source[fixed])
                        or not geometry_audit(bb,parent,item['start'],20)['valid']
                        or (kind=='noop' and not np.array_equal(bb,parent))):raise ValueError('Saved numerical closure control failed')
            for arm in arms:
                bb=out[arm+'/'+ident+'/backbone'][0];posed=out['pose/'+arm+'/'+ident][:]
                error=float(np.max(np.abs(posed-(bb.astype(np.float64)@ROTATION+OFFSET))))
                logged=next(r for r in m['controls'] if r['kind']=='pose' and r['arm']==arm and r['target_id']==ident)
                if error>.005 or error!=logged['max_abs']:raise ValueError('Saved proper-pose control failed')
        for row in c['selected']:
            ident=row['id'];item=dict(items[ident],id=ident)
            for arm in arms:
                reference='native_direct' if arm=='native_cond' else 'parent'
                backbones=out[arm+'/'+ident+'/backbone'][:]
                if backbones.shape!=(4,row['length'],4,3):raise ValueError('Malformed closure output')
                for slot,bb in enumerate(backbones):
                    source=src[arm+'/'+ident+'/backbone'][slot];parent=src[reference+'/'+ident+'/backbone'][slot]
                    records.append(score(bb,source,parent,item,arm,slot,row['bucket']))
        prefix_error=None
        if not c['profile_only']:
            with h5py.File(c['profile_predictions']) as before:
                prefix_error=max(float(np.max(np.abs(out[a+'/'+i+'/backbone'][:]-before[a+'/'+i+'/backbone'][:]))) for a in arms for i in c['profile_ids'])
            if prefix_error!=0:raise ValueError('Profile/full CPU outputs changed')
    summary=[]
    for arm in arms:
        rr=[r for r in records if r['arm']==arm]
        summary.append(dict(arm=arm,samples=len(rr),coarse_valid=sum(r['coarse_valid'] for r in rr),
            connected_raw=sum(r['connected_raw'] for r in rr),qualified_raw=sum(r['qualified_raw'] for r in rr),
            local_geometry=sum(r['local_geometry']['valid'] for r in rr),
            mean_max_atom_displacement=float(np.mean([r['max_atom_displacement'] for r in rr]))))
    recommended=math.ceil(sum(r['seconds'] for r in m['records'])*384/len(records)*1.5+sum(r['seconds'] for r in m['controls'])+120)
    qualified=recommended<=spec['execution']['full_work_cap_seconds'] if c['profile_only'] else next(r['qualified_raw'] for r in summary if r['arm']=='generated_cond')>=45
    return dict(status='complete',profile_only=c['profile_only'],numerically_qualified=True,qualified=qualified,
        manifest_path=str(mp.resolve()),manifest_sha256=sha(mp),predictions_sha256=sha(run/'predictions.h5'),protocol_sha256=sha(c['protocol']),
        elapsed_seconds=m['elapsed_seconds'],estimated_full_seconds=recommended,controls=20,prefix_max_abs=prefix_error,
        summary=summary,records=records,scope='CPU-only local closure; fixed motif and far scaffold, generated-parent geometry targets. Native arm explicitly oracle. All failures retained. Geometric feasibility alone does not establish designability or same-refold motif/global/scaffold agreement.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(a.run);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');visible={k:v for k,v in d.items() if k!='records'}
    a.output.with_suffix('.md').write_text('# Local backbone closure\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))


if __name__=='__main__':main()
