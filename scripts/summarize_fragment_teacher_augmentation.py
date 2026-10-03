"""Audit every accepted and rejected condition/state pair before training."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from fragment_teacher_augmentation_core import qualifying_states,maximum_scaffold_difference
from prepare_fragment_teacher_augmentation import audit_config
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),training_gate_passed=False)
    c=m['config'];audit_config(c)
    if m['training_updates_executed'] or m['targets_sha256']!=sha(run/'targets.h5') or m['peak_reserved_GiB']>75:raise ValueError('Changed data job outputs')
    index={(r['target_id'],r['condition']):r for r in m['records']};rows=[];wanted_controls=set()
    if len(index)!=1152 or len(m['records'])!=1152:raise ValueError('Changed full condition coverage')
    with h5py.File(c['candidates']) as src,h5py.File(c['fragments']) as fr,h5py.File(run/'targets.h5') as out:
        if set(out)!=set(src):raise ValueError('Changed full protein coverage')
        for ident,g in src.items():
            target=out[ident];states=g['state_indices'][:]
            if set(target['retained'])!=set(g['conditions']) or not np.array_equal(target['state_indices'][:],states):raise ValueError('Changed states or conditions')
            if len(states):
                wanted_controls.add(ident);bb=target['roundtrip'][:];source=g['teacher_backbone'][:]
                if not np.array_equal(target['teacher_z'][:],g['teacher_z'][:]) or not np.array_equal(target['teacher_backbone'][:],source) or bb.shape!=source.shape or not np.isfinite(bb).all():raise ValueError('Changed endpoint tensors')
            for condition,q in fr['train/'+ident+'/conditions'].items():
                base=g['conditions/'+condition][:];accepted,checks=qualifying_states(bb,source,q['fragment'][:],int(q.attrs['start']),base) if len(base) else ([],[])
                recorded=index[ident,condition]['candidates']
                if len(checks)!=len(recorded) or any(any(x[k]!=y[k] for k in ('candidate_index','coarse_valid','accepted')) or any(abs(x[k]-y[k])>1e-5 for k in ('whole_rmsd','motif_ca_rmsd','motif_drms')) for x,y in zip(checks,recorded)) or not np.array_equal(target['retained/'+condition][:],accepted) or len(accepted)!=index[ident,condition]['retained']:raise ValueError('Changed endpoint quality decision')
                difference=maximum_scaffold_difference(bb,accepted,int(q.attrs['start']),len(q['fragment'])) if len(accepted)>=2 else None
                rows.append(dict(target_id=ident,condition=condition,source_states=len(base),retained_states=len(accepted),max_scaffold_rmsd=difference))
    controls=m['controls']
    if len(controls)!=len(wanted_controls) or {r['target_id'] for r in controls}!=wanted_controls or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in controls):raise ValueError('Missing or failed repeat controls')
    multiple={r['target_id'] for r in rows if r['retained_states']>=2};diverse={r['target_id'] for r in rows if r['max_scaffold_rmsd'] is not None and r['max_scaffold_rmsd']>1};gate=len(multiple)>=64 and len(diverse)>=32
    return dict(status='complete',manifest_sha256=sha(path),targets_sha256=m['targets_sha256'],training_gate_passed=gate,proteins=128,conditions=1152,source_condition_state_pairs=sum(r['source_states'] for r in rows),retained_condition_state_pairs=sum(r['retained_states'] for r in rows),eligible_conditions=sum(r['retained_states']>0 for r in rows),proteins_with_multiple_states=len(multiple),proteins_with_scaffold_pair_over_1A=len(diverse),repeat_controls=len(controls),peak_reserved_GiB=m['peak_reserved_GiB'],elapsed_seconds=m['elapsed_seconds'],records=rows,scope='Training-only endpoints. Original examples remain available for every condition. Roundtrip quality and diversity do not establish generated-sample designability; matched downstream refolding is required.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Compatible teacher endpoint augmentation\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')


if __name__=='__main__':main()
