"""Matched, training-family comparisons for the small teacher-capacity test."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs=3,type=Path,required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();runs={};matched=[]
    for path in a.runs:
        m=json.loads((path/'manifest.json').read_text());c=dict(m['config']);arm=c.pop('arm');runs[arm]=m;matched.append(c)
        if m['status'] not in ('running','complete') or m['updates']<a.step:raise ValueError('checkpoint not reached')
    if set(runs)!={'reference','aligned_teacher','pca_teacher'} or not all(x==matched[0] for x in matched) or len({m['initial_checkpoint_sha256'] for m in runs.values()})!=1:raise ValueError('unmatched experiments')
    logs=[]
    for m in runs.values():logs.append([{k:r[k] for k in ('step','length','batch','learning_rate','ids_sha256','label_choices_sha256')} for r in m['training'] if r['step']<=a.step])
    if not all(x==logs[0] for x in logs):raise ValueError('training draws differ')
    metrics=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','valid_teacher_hit_fraction','state_total_variation');d=dict(step=a.step,matched=True,comparisons={},summaries={})
    def scores(m,step,guidance):
        rows=[r for r in m['scores'] if r['step']==step and r['guidance']==guidance]
        if len(rows)!=32 or len({r['target_id'] for r in rows})!=32:raise ValueError('incomplete scoring')
        return {r['target_id']:dict(r,coverage32=r['coverage']['32'],strict_coverage32=r['strict_coverage']['32']) for r in rows}
    lines=['# Matched small-ensemble learning comparison','',f'Checkpoint: {a.step}. Same initialization, labels, target batches and random label draws verified. Teacher arms differ only in coordinate frame.','', 'Teacher-defined training states only; no biological-state or generalization claim. CFG settings and both contact thresholds remain visible.','', '| Arm / guidance | Recall @2A | Recall @1A | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV |','|---|---:|---:|---:|---:|---:|---:|']
    for guidance in (1,2):
        reference=scores(runs['reference'],a.step,guidance);initial=[scores(m,0,guidance) for m in runs.values()]
        if not all(x==initial[0] for x in initial):raise ValueError('different initialization predictions')
        for arm,m in runs.items():
            cand=scores(m,a.step,guidance);key=f'{arm}_cfg{guidance}';d['summaries'][key]={metric:float(np.mean([r[metric] for r in cand.values()])) for metric in metrics};v=d['summaries'][key]
            lines.append(f"| {key} | {v['coverage32']:.5f} | {v['strict_coverage32']:.5f} | {v['valid_fraction']:.5f} | {v['teacher_ca_lddt']:.5f} | {v['reference_ca_lddt']:.5f} | {v['state_total_variation']:.5f} |")
            for name,other in [('initial',initial[0]),('reference',reference),('pca',scores(runs['pca_teacher'],a.step,guidance))]:d['comparisons'][f'{key}_vs_{name}']={metric:paired_comparison({i:r[metric] for i,r in cand.items()},{i:r[metric] for i,r in other.items()}) for metric in metrics}
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
