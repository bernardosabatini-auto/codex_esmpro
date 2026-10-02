"""Paired prior comparisons at both seeds of the122-family experiment."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from compare_overfit_balanced import scored
from latentfold.teacher_states import audited_families,paired_change
from latentfold.training_schedule import proportional_schedule


def compare(manifests,step):
    if step not in (500,2000) or len(manifests)!=4:raise ValueError('four runs at a declared checkpoint required')
    runs={};normalized=[]
    for m in manifests:
        c=m['config'];key=(c['seed'],c['label_distribution'])
        if key in runs or c['arm']!='aligned_teacher' or c['profile_only'] or c['evaluation_guidance']!=[1]:raise ValueError('invalid or duplicate expanded arm')
        if m['status'] not in ('running','complete') or m['updates']<step:raise ValueError('checkpoint not reached')
        if sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('protocol changed')
        if m['initial_checkpoint_sha256']!=c['checkpoint_sha256']:raise ValueError('initial weights changed')
        runs[key]=m;normalized.append({k:v for k,v in c.items() if k not in ('seed','label_distribution')})
    if not all(c==normalized[0] for c in normalized):raise ValueError('unmatched expanded configurations')
    c=manifests[0]['config'];protocol=json.loads(Path(c['protocol']).read_text());seeds=protocol['seeds']
    if set(runs)!={(seed,prior) for seed in seeds for prior in ('empirical','balanced')} or len(seeds)!=2:raise ValueError('both priors at both declared seeds required')
    families=audited_families(c);inventory=json.loads(Path(c['corpus_inventory']).read_text());targets={r['id']:r for r in inventory['targets']}
    if len(targets)!=122 or len(set(families.values()))!=122 or len(set(inventory['capacity_ids']))!=32 or not set(inventory['capacity_ids'])<=set(targets):raise ValueError('invalid cohort coverage')
    counts={length:sum(r['bucket']==length for r in targets.values()) for length in (128,256,384,512)}
    expected_steps=[s+1 for s in range(step) if s%25==0 or s+1 in c['evaluation_steps']]
    for seed in seeds:
        expected=proportional_schedule(counts,c['updates'],seed+2);logs=[]
        for prior in ('empirical','balanced'):
            m=runs[seed,prior]
            if m['length_schedule']!=expected:raise ValueError('wrong target-proportional length schedule')
            log=[{k:r[k] for k in ('step','length','batch','learning_rate','ids_sha256')} for r in m['training'] if r['step']<=step]
            if [r['step'] for r in log]!=expected_steps:raise ValueError('missing training draw logs')
            if any(r['length']!=expected[r['step']-1] or r['batch']!=c['batches'][str(r['length'])] for r in log):raise ValueError('logged batches disagree with schedule')
            logs.append(log)
        if logs[0]!=logs[1]:raise ValueError('target order or learning rates differ within seed')
    metrics=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','state_total_variation','balanced_state_tv','singleton_coverage')
    initial=scored(manifests[0],0,1,targets)
    for m in manifests:
        other=scored(m,0,1,targets)
        for ident,r in other.items():
            if r['assignments']!=initial[ident]['assignments'] or any(not np.isclose(r[k],initial[ident][k],atol=1e-6,rtol=1e-6) for k in metrics if r[k] is not None):raise ValueError('different initialization predictions')
    cohorts=dict(all122=set(targets),original32=set(inventory['capacity_ids']),additional90=set(targets)-set(inventory['capacity_ids']))
    d=dict(step=step,matched=True,seeds=seeds,summaries={},comparisons={},capacity_checks={})
    for seed in seeds:
        current={prior:scored(runs[seed,prior],step,1,targets) for prior in ('empirical','balanced')}
        for cohort,ids in cohorts.items():
            for prior,rows in current.items():
                name=f'{seed}_{prior}_{cohort}'
                summary={}
                for key in metrics:
                    values=[rows[i][key] for i in sorted(ids) if rows[i][key] is not None]
                    summary[key]=float(np.mean(values)) if values else None
                d['summaries'][name]=summary
                for label,reference in [('initial',initial)]+([('empirical',current['empirical'])] if prior=='balanced' else []):
                    values={}
                    for key in metrics:
                        eligible=sorted(i for i in ids if rows[i][key] is not None)
                        if not eligible:values[key]=None;continue
                        a={i:rows[i][key] for i in eligible};b={i:reference[i][key] for i in eligible}
                        if not all(np.isfinite(v) for v in list(a.values())+list(b.values())):raise ValueError('nonfinite scores')
                        values[key]=paired_change(a,b,families={i:families[i] for i in eligible})
                    d['comparisons'][name+'_vs_'+label]=values
        a=d['comparisons'][f'{seed}_balanced_all122_vs_initial'];b=d['comparisons'][f'{seed}_balanced_all122_vs_empirical']
        checks=dict(positive_recall_ci_vs_initial=a['coverage32']['ci95'][0]>0,positive_recall_ci_vs_empirical=b['coverage32']['ci95'][0]>0,validity_vs_initial=a['valid_fraction']['difference']>=-.01,validity_vs_empirical=b['valid_fraction']['difference']>=-.01)
        d['capacity_checks'][str(seed)]=dict(checks=checks,passed=all(checks.values()))
    d['replicated_capacity_passed']=all(r['passed'] for r in d['capacity_checks'].values())
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,nargs=4,required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=compare([json.loads((path/'manifest.json').read_text()) for path in a.runs],a.step)
    lines=['# Replicated122-family teacher-prior comparison','',f"Checkpoint{a.step}; matched configurations, schedules, within-seed target/LR logs and initialization predictions verified. Both declared seeds retained.",'','All cohorts below are training data, including the additional90 proteins. Teacher modes are predictions, not experimental states. Geometry failures remain in denominators. Intervals resample families and are unadjusted.','','| Seed / prior / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Empirical TV | Balanced TV |','|---|---:|---:|---:|---:|---:|---:|']
    for name,r in d['summaries'].items():lines.append(f"| {name} | {r['coverage32']:.5f} | {r['strict_coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['state_total_variation']:.5f} | {r['balanced_state_tv']:.5f} |")
    lines+=['','| Full122 balanced comparison | Recall difference |95% interval | Validity difference |','|---|---:|---|---:|']
    for name,r in d['comparisons'].items():
        if 'balanced_all122' in name:lines.append(f"| {name} | {r['coverage32']['difference']:+.5f} | {r['coverage32']['ci95']} | {r['valid_fraction']['difference']:+.5f} |")
    for seed,r in d['capacity_checks'].items():lines+=['',f"Seed{seed} capacity criteria: {r['passed']}; {r['checks']}."]
    lines+=['',f"Replicated capacity criteria passed: {d['replicated_capacity_passed']}.",'Separate accuracy, experimental-state ensemble coverage and matched timing remain required; this training-data analysis cannot promote a model. The broader criteria do not replace the original32/reference-control gate.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
