"""Matched five-arm comparison of teacher priors and coordinate frames."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import audited_families,paired_change


EXPECTED={('reference','empirical'),('aligned_teacher','empirical'),
          ('pca_teacher','empirical'),('aligned_teacher','balanced'),('pca_teacher','balanced')}


def validate_runs(manifests,step):
    runs={};configs=[]
    for m in manifests:
        c=dict(m['config']);key=(c.pop('arm'),c.pop('label_distribution','empirical'))
        if key in runs:raise ValueError('duplicate arm/prior')
        runs[key]=m
        if m['status'] not in ('running','complete') or m['updates']<step:raise ValueError('checkpoint not reached')
        for name in ('followup_protocol','followup_protocol_sha256'):c.pop(name,None)
        configs.append(c)
    if set(runs)!=EXPECTED or not all(c==configs[0] for c in configs):raise ValueError('unmatched configurations')
    if len({m['initial_checkpoint_sha256'] for m in manifests})!=1:raise ValueError('different initial weights')
    fields=('step','length','batch','learning_rate','ids_sha256')
    logs=[[{k:r[k] for k in fields} for r in m['training'] if r['step']<=step] for m in manifests]
    expected_steps=[s+1 for s in range(step) if s%25==0 or s+1 in configs[0]['evaluation_steps']]
    if any([r['step'] for r in log]!=expected_steps for log in logs) or not all(log==logs[0] for log in logs):raise ValueError('missing or unmatched target/LR draws')
    for prior in ('empirical','balanced'):
        draws=[[r['label_choices_sha256'] for r in m['training'] if r['step']<=step] for (arm,p),m in runs.items() if p==prior]
        if not all(x==draws[0] for x in draws):raise ValueError('label draws differ within prior')
    return runs


def scored(m,step,guidance,targets):
    rows=[r for r in m['scores'] if r['step']==step and r['guidance']==guidance]
    if len(rows)!=len(targets) or {r['target_id'] for r in rows}!=set(targets):raise ValueError('incomplete scores')
    result={}
    for r in rows:
        a=np.asarray(r['assignments']);counts=np.bincount(targets[r['target_id']]['state_definition']['clusters'])
        if len(a)!=32 or (a < -1).any() or (a>=len(counts)).any():raise ValueError('invalid sample assignments')
        q=np.array([(a==i).mean() for i in range(len(counts))]);rare=counts==1
        result[r['target_id']]=dict(r,coverage32=r['coverage']['32'],strict_coverage32=r['strict_coverage']['32'],
            balanced_state_tv=float(.5*(np.abs(q-1/len(counts)).sum()+(a<0).mean())),
            singleton_coverage=float((q[rare]>0).mean()) if rare.any() else None)
    return result


def compare(manifests,step):
    runs=validate_runs(manifests,step);c=next(iter(runs.values()))['config'];families=audited_families(c)
    targets={r['id']:r for r in json.loads(Path(c['label_manifest']).read_text())['config']['targets']}
    protocols=set()
    for (arm,prior),m in runs.items():
        if prior=='balanced':
            c=m['config'];digest=hashlib.sha256(Path(c['followup_protocol']).read_bytes()).hexdigest()
            if digest!=c['followup_protocol_sha256']:raise ValueError('changed balanced protocol')
            protocols.add(digest)
    if len(protocols)!=1:raise ValueError('different follow-up protocols')
    metrics=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','state_total_variation','balanced_state_tv','singleton_coverage')
    result=dict(step=step,matched=True,protocol_sha256=next(iter(protocols)),summaries={},comparisons={})
    for guidance in (1,2):
        initial=scored(runs[('reference','empirical')],0,guidance,targets)
        current={key:scored(m,step,guidance,targets) for key,m in runs.items()}
        for m in runs.values():
            other=scored(m,0,guidance,targets)
            for ident,r in other.items():
                if r['assignments']!=initial[ident]['assignments'] or any(not np.isclose(r[k],initial[ident][k],atol=1e-6,rtol=1e-6) for k in metrics if r[k] is not None):raise ValueError('initial predictions differ')
        for (arm,prior),rows in current.items():
            name=f'{arm}_{prior}_cfg{guidance}'
            result['summaries'][name]={k:float(np.mean([r[k] for r in rows.values() if r[k] is not None])) for k in metrics}
            comparators=dict(initial=initial,reference=current[('reference','empirical')])
            if prior=='balanced':comparators['empirical_same_frame']=current[(arm,'empirical')]
            if arm=='aligned_teacher':comparators['pca_same_prior']=current[('pca_teacher',prior)]
            for label,other in comparators.items():
                paired={}
                for metric in metrics:
                    ids=[i for i in rows if rows[i][metric] is not None]
                    paired[metric]=paired_change({i:rows[i][metric] for i in ids},{i:other[i][metric] for i in ids},families={i:families[i] for i in ids})
                result['comparisons'][f'{name}_vs_{label}']=paired
    decisions=json.loads((Path(__file__).resolve().parents[1]/'configs/overfit_decisions.json').read_text())
    result['capacity_checks']={}
    for arm in ('aligned_teacher','pca_teacher'):
        name=f"{arm}_balanced_cfg{decisions['primary_guidance']}"
        r=result['comparisons'][name+'_vs_reference']['coverage32'];i=result['comparisons'][name+'_vs_initial']
        checks=dict(recall_gain=r['difference']>=decisions['minimum_recall_gain_vs_reference'],positive_ci_vs_reference=r['ci95'][0]>0,positive_ci_vs_initial=i['coverage32']['ci95'][0]>0,validity_margin=i['valid_fraction']['difference']>=decisions['minimum_validity_delta_vs_initial'])
        result['capacity_checks'][arm]=dict(checks=checks,passed=all(checks.values()))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',nargs=5,type=Path,required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();d=compare([json.loads((p/'manifest.json').read_text()) for p in a.runs],a.step)
    lines=['# Matched teacher-prior and frame comparison','',f"Checkpoint: {a.step}. Initialization, target order, learning-rate schedule, configurations and within-prior label draws verified. Both balanced arms use the same frozen protocol.",'',
           'Training-only teacher states. Paired family intervals are unadjusted; intermediate results are provisional. Singleton recall is averaged over proteins containing a singleton state. Equal-state sampling changes the target prior; both frequency comparisons remain visible.','',
           '| Arm / prior / CFG | Recall @2A | Recall @1A | Valid | Teacher CA-lDDT | Empirical TV | Balanced TV | Singleton recall |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name,v in d['summaries'].items():lines.append(f"| {name} | {v['coverage32']:.5f} | {v['strict_coverage32']:.5f} | {v['valid_fraction']:.5f} | {v['teacher_ca_lddt']:.5f} | {v['state_total_variation']:.5f} | {v['balanced_state_tv']:.5f} | {v['singleton_coverage']:.5f} |")
    lines+=['','| Primary CFG1 comparison | Recall difference | Paired 95% interval | Validity difference |','|---|---:|---|---:|']
    for name,c in d['comparisons'].items():
        if 'balanced_cfg1' in name:lines.append(f"| {name} | {c['coverage32']['difference']:+.5f} | {c['coverage32']['ci95']} | {c['valid_fraction']['difference']:+.5f} |")
    for arm,c in d['capacity_checks'].items():lines+=['',f"{arm} original capacity screen: {'PASS' if c['passed'] else 'NOT PASSED'}; {c['checks']}."]
    lines+=['','No result here establishes biological populations, unseen-family performance, or a faster deployable model.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
