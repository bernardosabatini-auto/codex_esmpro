"""Matched tail versus full-network balanced adaptation at two declared seeds."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from compare_overfit_balanced import scored
from latentfold.teacher_states import audited_families,paired_change
from latentfold.training_schedule import proportional_schedule

METRICS=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','balanced_state_tv')
EXCEPTIONS={'protocol','protocol_sha256','followup_protocol','followup_protocol_sha256','profile_report','profile_report_sha256','work_cap_seconds','trainable_tail_blocks'}

def matched(full,tail,step,intervention='tail'):
    a,b=full['config'],tail['config']
    if intervention not in ('tail','local_geometry') or step not in (500,2000) or a.get('trainable_tail_blocks') is not None or a.get('local_geometry'):raise ValueError('invalid intervention')
    exceptions=EXCEPTIONS
    if intervention=='tail':
        if b.get('trainable_tail_blocks')!=4 or b.get('local_geometry'):raise ValueError('invalid tail intervention')
    else:
        if b.get('trainable_tail_blocks') is not None or not b.get('local_geometry'):raise ValueError('invalid geometry intervention')
        exceptions=EXCEPTIONS|{'local_geometry'}
    if {k:v for k,v in a.items() if k not in exceptions}!={k:v for k,v in b.items() if k not in exceptions}:raise ValueError('unmatched configurations')
    if a['profile_only'] or a['label_distribution']!='balanced' or a['arm']!='aligned_teacher' or a['evaluation_guidance']!=[1]:raise ValueError('wrong training scope')
    for m in (full,tail):
        c=m['config']
        if m['status'] not in ('running','complete') or m['updates']<step:raise ValueError('endpoint not ready')
        for key in ('protocol','followup_protocol','profile_report'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
        if m['initial_checkpoint_sha256']!=c['checkpoint_sha256']:raise ValueError('initial checkpoint changed')
    if intervention=='tail':
        check=tail.get('training_subset',{})
        if not check.get('frozen_unchanged') or check.get('verified_update',0)<step:raise ValueError('frozen weight check not ready or failed')
        if check['initial_frozen_sha256']!=check['final_frozen_sha256'] or check['initial_frozen_sha256']!=check['ema_frozen_sha256']:raise ValueError('frozen hashes differ')
    else:
        recipe=json.loads(Path(b['protocol']).read_text())
        if b['local_geometry']!=recipe['local_geometry']:raise ValueError('changed auxiliary recipe')
        rows=[r for r in tail.get('local_geometry_updates',[]) if r['step']<=step]
        if len(rows)!=step or {r['step'] for r in rows}!=set(range(1,step+1)):raise ValueError('incomplete auxiliary logs')
        fields=('flow_parameter_grad_norm','aux_parameter_grad_norm','effective_geometry_weight','aux_to_flow_ratio','geometry_loss')
        if any(not np.isfinite(r[k]) or r[k]<0 for r in rows for k in fields) or any(r['flow_parameter_grad_norm']<=0 or r['aux_to_flow_ratio']>.100001 for r in rows):raise ValueError('auxiliary gradient control failed')
    inventory=json.loads(Path(a['corpus_inventory']).read_text());targets={r['id']:r for r in inventory['targets']};families=audited_families(a)
    if len(targets)!=122 or len(set(families.values()))!=122 or len(set(inventory['capacity_ids']))!=32:raise ValueError('wrong corpus')
    expected=proportional_schedule({k:sum(r['bucket']==k for r in targets.values()) for k in (128,256,384,512)},a['updates'],a['seed']+2)
    steps=[s+1 for s in range(step) if s%25==0 or s+1 in a['evaluation_steps']]
    logs=[]
    for m in (full,tail):
        if m['length_schedule']!=expected:raise ValueError('wrong length schedule')
        rows=[{k:r[k] for k in ('step','length','batch','learning_rate','ids_sha256','label_choices_sha256')} for r in m['training'] if r['step']<=step]
        if [r['step'] for r in rows]!=steps:raise ValueError('missing draw logs')
        if any(r['length']!=expected[r['step']-1] or r['batch']!=a['batches'][str(r['length'])] for r in rows):raise ValueError('wrong batch logs')
        logs.append(rows)
    if logs[0]!=logs[1]:raise ValueError('target, label or LR draws differ')
    initial=scored(full,0,1,targets);other=scored(tail,0,1,targets)
    for ident,r in initial.items():
        tolerance=1e-6 if intervention=='tail' else 1e-5
        if r['assignments']!=other[ident]['assignments'] or any(not np.isclose(r[k],other[ident][k],atol=tolerance,rtol=1e-6 if intervention=='tail' else 0) for k in METRICS):raise ValueError('initial predictions differ')
    return targets,families,inventory,initial


def compare(full,tail,step):
    recipe=json.loads(Path(tail[0]['config']['protocol']).read_text());seeds=recipe['seeds']
    if len(full)!=2 or len(tail)!=2 or len(seeds)!=2 or {m['config']['seed'] for m in full}!={*seeds} or {m['config']['seed'] for m in tail}!={*seeds}:raise ValueError('both declared seeds required')
    d=dict(step=step,matched=True,seeds=seeds,summaries={},comparisons={})
    for seed in seeds:
        f=next(m for m in full if m['config']['seed']==seed);t=next(m for m in tail if m['config']['seed']==seed)
        targets,families,inventory,initial=matched(f,t,step)
        values=dict(full=scored(f,step,1,targets),tail=scored(t,step,1,targets),initial=initial)
        cohorts=dict(all122=set(targets),original32=set(inventory['capacity_ids']),additional90=set(targets)-set(inventory['capacity_ids']))
        for cohort,ids in cohorts.items():
            for arm,rows in values.items():d['summaries'][f'{seed}_{arm}_{cohort}']={key:float(np.mean([rows[i][key] for i in sorted(ids)])) for key in METRICS}
            for reference in ('full','initial'):
                d['comparisons'][f'{seed}_tail_{cohort}_vs_{reference}']={key:paired_change({i:values['tail'][i][key] for i in sorted(ids)},{i:values[reference][i][key] for i in sorted(ids)},families={i:families[i] for i in ids}) for key in METRICS}
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--full',nargs=2,type=Path,required=True);p.add_argument('--tail',nargs=2,type=Path,required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=compare(*[[json.loads((r/'manifest.json').read_text()) for r in paths] for paths in (a.full,a.tail)],a.step)
    lines=['# Restricted versus full-network balanced adaptation','',f'Checkpoint {a.step}; both seeds retained. Configurations, initial predictions, target/label/LR logs and frozen raw/EMA hashes verified. All cohorts are training data; biological diversity and generalization require separate evaluation.','','| Seed / arm / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |','|---|---:|---:|---:|---:|---:|']
    for name,r in d['summaries'].items():lines.append(f"| {name} | {r['coverage32']:.5f} | {r['strict_coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['balanced_state_tv']:.5f} |")
    for name,r in d['comparisons'].items():
        if 'all122' in name:lines+=['',f"{name}: recall delta {r['coverage32']['difference']:+.5f}, 95% interval {r['coverage32']['ci95']}; validity delta {r['valid_fraction']['difference']:+.5f}."]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
