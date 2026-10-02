"""Capacity retention under frozen-field replay, compared with both full427 controls."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from expansion_corpus import metadata
from compare_expansion_training import verify_draws
from compare_overfit_balanced import scored
from latentfold.teacher_states import paired_change


REPLAY_KEYS={'functional_replay','replay_protocol','replay_protocol_sha256','replay_selection','replay_selection_sha256','replay_checkpoint','replay_checkpoint_sha256'}
RESOURCE_KEYS={'profile_report','profile_report_sha256','work_cap_seconds','allocation_minutes'}


def validate_pair(full,candidate,step):
    fc,cc=full['config'],candidate['config']
    if step not in (500,2000) or fc.get('functional_replay') or not cc.get('functional_replay'):raise ValueError('wrong replay/control identity')
    stripped=lambda c:{k:v for k,v in c.items() if k not in REPLAY_KEYS|RESOURCE_KEYS}
    if stripped(fc)!=stripped(cc):raise ValueError('replay changes primary recipe')
    for m in (full,candidate):
        if m['status'] not in ('running','complete') or m['updates']<step or m['initial_checkpoint_sha256']!=cc['checkpoint_sha256']:raise ValueError('incomplete or different initialization')
    for key in ('replay_protocol','replay_selection'):
        if sha(cc[key])!=cc[key+'_sha256']:raise ValueError('changed '+key)
    recipe=json.loads(Path(cc['replay_protocol']).read_text());r=candidate['functional_replay'];updates=[x for x in r['updates'] if x['step']<=step]
    if not r['reference_unchanged'] or r['verified_update']<step or r['reference_initial_sha256']!=r['reference_final_sha256'] or len(r['controls'])!=4 or {x['bucket'] for x in r['controls']}!={128,256,384,512}:raise ValueError('frozen replay identity failed')
    if any(x['max_velocity_error']>1e-6 or x['replay_loss']>1e-12 for x in r['controls']):raise ValueError('initial field mismatch')
    if len(updates)!=step or [x['step'] for x in updates]!=list(range(1,step+1)):raise ValueError('incomplete replay updates')
    for x in updates:
        if any(not np.isfinite(x[k]) or x[k]<0 for k in ('primary_gradient_norm','replay_gradient_norm','replay_to_primary_ratio','effective_weight','replay_loss')) or x['primary_gradient_norm']<=0 or x['replay_to_primary_ratio']>recipe['replay']['maximum_gradient_ratio']+1e-6 or x['effective_weight']>recipe['replay']['maximum_weight']:raise ValueError('invalid replay gradient accounting')


def compare(full,candidates,step):
    if len(full)!=2 or len(candidates)!=2:raise ValueError('both seeds required')
    full={m['config']['seed']:m for m in full};candidates={m['config']['seed']:m for m in candidates}
    if set(full)!=set(candidates) or set(full)!={2026100171,2026100181}:raise ValueError('missing or duplicate declared seed')
    inv=metadata(candidates[2026100171]['config']);rows={r['id']:r for r in inv['targets']};targets={i:rows[i] for i in inv['evaluation_ids']};families={i:r['family'] for i,r in targets.items()}
    metrics=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','balanced_state_tv')
    d=dict(status='complete',step=step,seeds=sorted(full),training_targets=len(rows),matched=True,summaries={},comparisons={},capacity_checks={})
    protocol_hashes=set();selections=set()
    for seed,m in candidates.items():
        baseline=full[seed];validate_pair(baseline,m,step);c=m['config'];protocol_hashes.add(c['replay_protocol_sha256']);selections.add(c['replay_selection_sha256'])
        if c['corpus_inventory_sha256']!=candidates[2026100171]['config']['corpus_inventory_sha256']:raise ValueError('different candidate corpus')
        verify_draws(baseline,inv,step);verify_draws(m,inv,step)
        initial=scored(baseline,0,1,targets);other=scored(m,0,1,targets)
        if any(initial[i]['assignments']!=other[i]['assignments'] or any(not np.isclose(initial[i][k],other[i][k],atol=1e-6,rtol=0) for k in metrics) for i in targets):raise ValueError('initial predictions differ')
        values=dict(full=scored(baseline,step,1,targets),replay=scored(m,step,1,targets),initial=initial)
        cohorts=dict(all64=list(targets),original32=[i for i in targets if targets[i]['cohort']=='original122'],new32=[i for i in targets if targets[i]['cohort']!='original122'])
        for cohort,ids in cohorts.items():
            for kind,group in values.items():d['summaries'][f'{seed}_{cohort}_{kind}']={k:float(np.mean([group[i][k] for i in ids])) for k in metrics}
            for reference in ('full','initial'):d['comparisons'][f'{seed}_{cohort}_vs_{reference}']={k:paired_change({i:values['replay'][i][k] for i in ids},{i:values[reference][i][k] for i in ids},families={i:families[i] for i in ids}) for k in metrics}
        r=d['comparisons'][f'{seed}_all64_vs_full'];checks=dict(recall_retained=r['coverage32']['ci95'][0]>-.05,validity_retained=r['valid_fraction']['difference']>=-.01)
        d['capacity_checks'][str(seed)]=dict(checks=checks,passed=all(checks.values()))
    if len(protocol_hashes)!=1 or len(selections)!=1:raise ValueError('different replay recipes or selections')
    d['replicated_capacity_retained']=all(r['passed'] for r in d['capacity_checks'].values());return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--full',type=Path,nargs=2,required=True);p.add_argument('--candidate',type=Path,nargs=2,required=True);p.add_argument('--step',type=int,choices=[500,2000],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();read=lambda ps:[json.loads((x/'manifest.json').read_text()) for x in ps];d=compare(read(a.full),read(a.candidate),a.step)
    lines=['# Functional replay capacity retention','',f"Checkpoint{a.step}; both matched427-family seeds, unchanged64-family training panel. Primary recipes, target/label/LR draws, initialization and frozen-reference controls verified. Retains capacity at both seeds:{d['replicated_capacity_retained']}.",'','All families are training data. No native or external qualification follows from capacity alone.','','| Seed / cohort / model | Recall@32 | Valid | Teacher CA-lDDT | Balanced TV |','|---|---:|---:|---:|---:|']
    for name,r in d['summaries'].items():lines.append(f"| {name} | {r['coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['balanced_state_tv']:.5f} |")
    for name,r in d['comparisons'].items():
        if 'all64' in name:lines+=['',f"{name}: recall delta{r['coverage32']['difference']:+.5f}, paired family95% interval{r['coverage32']['ci95']}; validity delta{r['valid_fraction']['difference']:+.5f}."]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
