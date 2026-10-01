"""Descriptive state-frequency diagnostics; retain empirical and balanced priors."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',nargs='+',type=Path,required=True)
    p.add_argument('--step',type=int,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();summaries={};all_states=[]
    lines=['# Teacher-state frequency diagnostic','',
           'Descriptive pooled-state counts; no biological-population claim. State definitions and all samples are unchanged. Original empirical-teacher frequencies and the alternative equal-state prior are both retained.','',
           '| Model / update / CFG | State frequency class | States | Hit fraction | Mean predicted probability | Mean teacher probability |',
           '|---|---|---:|---:|---:|---:|']
    for run in a.runs:
        m=json.loads((run/'manifest.json').read_text());c=m['config'];families=audited_families(c)
        targets={r['id']:r for r in json.loads(Path(c['label_manifest']).read_text())['config']['targets']}
        for step in sorted({0,a.step}):
            for guidance in (1,2):
                rows=[r for r in m['scores'] if r['step']==step and r['guidance']==guidance]
                if len(rows)!=len(families) or {r['target_id'] for r in rows}!=set(families):raise ValueError('incomplete scores')
                name=f"{c['arm']}_{c.get('label_distribution','empirical')}_{step}_cfg{guidance}"
                states=[];balanced_tv=[]
                for r in rows:
                    labels=np.array(targets[r['target_id']]['state_definition']['clusters'])
                    prior=np.bincount(labels)/len(labels);assignments=np.array(r['assignments'])
                    q=np.array([(assignments==state).mean() for state in range(len(prior))])
                    balanced_tv.append(float(.5*(np.abs(q-1/len(prior)).sum()+(assignments<0).mean())))
                    for state,prob in enumerate(prior):
                        states.append(dict(target=r['target_id'],family=families[r['target_id']],state=state,teacher_probability=float(prob),predicted_probability=float(q[state]),hit=bool(q[state]>0),ideal_hit_probability=float(1-(1-prob)**32)))
                summaries[name]=dict(empirical_state_tv=float(np.mean([r['state_total_variation'] for r in rows])),balanced_state_tv=float(np.mean(balanced_tv)),frequency_classes={})
                for category,low,hi in [('one_teacher',0,.0625),('two_teachers',.0625,.125),('intermediate',.125,.5),('majority',.5,1.)]:
                    group=[r for r in states if low<r['teacher_probability']<=hi]
                    if not group:continue
                    v=dict(states=len(group),**{k:float(np.mean([r[k] for r in group])) for k in ('hit','predicted_probability','teacher_probability','ideal_hit_probability')})
                    summaries[name]['frequency_classes'][category]=v
                    lines.append(f"| {name} | {category} | {v['states']} | {v['hit']:.5f} | {v['predicted_probability']:.5f} | {v['teacher_probability']:.5f} |")
                all_states.extend(dict(model=name,**r) for r in states)
    lines+=['','| Model / update / CFG | TV to empirical teacher prior | TV to equal-state prior |','|---|---:|---:|']
    for name,v in summaries.items():lines.append(f"| {name} | {v['empirical_state_tv']:.5f} | {v['balanced_state_tv']:.5f} |")
    a.output.with_suffix('.json').write_text(json.dumps(dict(summaries=summaries,states=all_states),indent=2)+'\n')
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
