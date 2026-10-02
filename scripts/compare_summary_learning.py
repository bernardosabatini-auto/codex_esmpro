"""Matched summary-versus-final learning test with a frozen replication decision."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import audited_families,paired_change
from compare_overfit_balanced import scored


def matched(manifests):
    arms={};configs=[]
    for m in manifests:
        c=dict(m['config']);arm=c.pop('summary_arm')
        if arm in arms or m['status']!='complete' or m['updates']!=500 or c['profile_only']:raise ValueError('missing completed matched arm')
        arms[arm]=m;configs.append(c)
    if set(arms)!={'projected_final','teacher_summary'} or len(configs)!=2 or configs[0]!=configs[1]:raise ValueError('different recipe beyond feature input')
    if len({m['initial_checkpoint_sha256'] for m in manifests})!=1 or len({m['summary_adapter']['initial_sha256'] for m in manifests})!=1:raise ValueError('different initial weights')
    fields=('step','length','batch','learning_rate','ids_sha256','label_choices_sha256')
    logs=[[{k:r[k] for k in fields} for r in m['training']] for m in manifests]
    expected=list(range(1,500,25))+[500]
    if any([r['step'] for r in rows]!=expected for rows in logs) or logs[0]!=logs[1]:raise ValueError('different or incomplete matched draws/LRs')
    for m in manifests:
        a=m['summary_adapter']
        if len(a['controls'])!=4 or not all(r['initial_exact'] for r in a['controls']) or len(a['gradients'])!=500 or any(not np.isfinite(r['norm']) or r['norm']<=0 for r in a['gradients']):raise ValueError('adapter controls failed')
        if len(m['scores'])!=64 or len(m['controls'])!=4:raise ValueError('evaluation incomplete')
    return arms,configs[0]


def compare(manifests):
    arms,c=matched(manifests)
    if sha(c['summary_protocol'])!=c['summary_protocol_sha256']:raise ValueError('changed learning protocol')
    protocol=json.loads(Path(c['summary_protocol']).read_text());families=audited_families(c)
    targets={r['id']:r for r in json.loads(Path(c['label_manifest']).read_text())['config']['targets']}
    baseline={arm:scored(m,0,1,targets) for arm,m in arms.items()}
    if baseline['teacher_summary']!=baseline['projected_final']:raise ValueError('initial predictions differ')
    final={arm:scored(m,500,1,targets) for arm,m in arms.items()}
    metrics=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','state_total_variation','balanced_state_tv','singleton_coverage')
    d=dict(status='complete',seed=c['seed'],matched=True,scope='All32 families are training data; teacher-defined states are predictions, not biological populations.',summaries={},comparisons={})
    groups=dict(initial=baseline['teacher_summary'],**final)
    for arm,rows in groups.items():d['summaries'][arm]={metric:float(np.mean([r[metric] for r in rows.values() if r[metric] is not None])) for metric in metrics}
    for other in ('initial','projected_final'):
        d['comparisons'][other]={}
        for metric in metrics:
            ids=[i for i in families if final['teacher_summary'][i][metric] is not None]
            d['comparisons'][other][metric]=paired_change({i:final['teacher_summary'][i][metric] for i in ids},{i:groups[other][i][metric] for i in ids},families={i:families[i] for i in ids})
    gate=protocol['advance_to_replication'];gain=d['comparisons']['projected_final'];initial=d['comparisons']['initial']
    checks=dict(recall_gain=gain['coverage32']['difference']>=gate['minimum_recall_gain_vs_projected_final'],positive_recall_interval=gain['coverage32']['ci95'][0]>0,validity_vs_control=gain['valid_fraction']['difference']>=gate['minimum_validity_delta_vs_projected_final'],validity_vs_initial=initial['valid_fraction']['difference']>=gate['minimum_validity_delta_vs_initial'])
    d.update(checks=checks,replication_justified=all(checks.values()))
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--step',type=int,choices=[500],default=500);p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=compare([json.loads((p/'manifest.json').read_text()) for p in a.runs])
    lines=['# Matched pretrained ESM-summary learning feasibility','',d['scope'],'',f"Seed{d['seed']}; initial predictions/weights and logged target/label/LR draws agree. Replication justified: {d['replication_justified']}.",'','| Arm | Recall@32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | Balanced TV |','|---|---:|---:|---:|---:|---:|']
    for arm,r in d['summaries'].items():lines.append(f"| {arm} | {r['coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['reference_ca_lddt']:.5f} | {r['balanced_state_tv']:.5f} |")
    for name,comp in d['comparisons'].items():
        r=comp['coverage32'];lines+=['',f"Mixture versus{name}: recall difference{r['difference']:+.5f}, paired family95% interval{r['ci95']}; validity difference{comp['valid_fraction']['difference']:+.5f}."]
    lines+=['',str(d['checks']),'','No native/external promotion follows from this training result. Retain all arms, failures and locked-test quarantine.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
