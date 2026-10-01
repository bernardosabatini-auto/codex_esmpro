"""Relate frozen-atlas student misses to fresh teacher recurrence, without filtering."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import audited_families,paired_change


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--teacher',type=Path,required=True);p.add_argument('--students',type=Path,nargs='+',required=True)
    p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    t=json.loads((a.teacher/'manifest.json').read_text());families=audited_families(t['config'])
    if t['status']!='complete' or len(t['scores'])!=64 or len(t['controls'])!=64:raise ValueError('complete recurrence required')
    teachers={mode:{r['target_id']:r for r in t['scores'] if r['mode']==mode} for mode in ('fixed_trunk','new_trunk')}
    if any(len(v)!=32 or set(v)!=set(families) or any(len(r['assignments'])!=32 for r in v.values()) for v in teachers.values()):raise ValueError('incomplete fresh teacher sample coverage')
    records={r['id']:r for r in json.loads(Path(t['config']['label_manifest']).read_text())['config']['targets']}
    d=dict(step=a.step,comparisons={},state_groups={})
    for run in a.students:
        m=json.loads((run/'manifest.json').read_text());c=m['config']
        if audited_families(c)!=families or c['label_manifest_sha256']!=t['config']['label_manifest_sha256']:raise ValueError('different state atlas')
        name=c['arm']+'_'+c.get('label_distribution','empirical')
        for step in (0,a.step):
            for cfg in (1,2):
                rows=[r for r in m['scores'] if r['step']==step and r['guidance']==cfg];students={r['target_id']:r for r in rows}
                if len(rows)!=32 or set(students)!=set(families) or any(len(r['assignments'])!=32 for r in rows):raise ValueError('incomplete student sample coverage')
                key=f'{name}_{step}_cfg{cfg}'
                if key in d['comparisons']:raise ValueError('duplicate student condition')
                getters={'recall':lambda r:r['coverage']['32'],'strict_recall':lambda r:r['strict_coverage']['32'],'valid_fraction':lambda r:r['valid_fraction'],'teacher_ca_lddt':lambda r:r['teacher_ca_lddt']}
                d['comparisons'][key]={mode:{metric:paired_change({i:get(r) for i,r in students.items()},{i:get(r) for i,r in teacher.items()},families=families) for metric,get in getters.items()} for mode,teacher in teachers.items()}
                groups={}
                for ident,r in records.items():
                    sizes=np.bincount(r['state_definition']['clusters'])
                    for state,size in enumerate(sizes):
                        hit=[state in teachers[mode][ident]['assignments'] for mode in ('fixed_trunk','new_trunk')]
                        recurrence='both' if all(hit) else 'fixed_only' if hit[0] else 'new_only' if hit[1] else 'neither'
                        group=('singleton' if size==1 else 'repeated')+'_'+recurrence
                        v=groups.setdefault(group,dict(states=0,student_hits=0));v['states']+=1;v['student_hits']+=int(state in students[ident]['assignments'])
                d['state_groups'][key]=groups
    lines=['# Student misses and fresh teacher recurrence','',
           'Post-hoc descriptive diagnosis on the unchanged32 training proteins and frozen teacher states. Both teachers and students draw32 samples, but their noise seeds are not paired across model types. Intervals pair sequence families only. Neither fresh teacher sampling nor student coverage establishes biological populations. No state is removed or reweighted by this analysis.','',
           '| Student / update / CFG | Teacher condition | Student recall | Fresh teacher recall | Student minus teacher | 95% family interval |','|---|---|---:|---:|---:|---|']
    for key,comparisons in d['comparisons'].items():
        for mode,metrics in comparisons.items():
            r=metrics['recall'];lines.append(f"| {key} | {mode} | {r['candidate']:.5f} | {r['reference']:.5f} | {r['difference']:+.5f} | {r['ci95']} |")
    lines+=['','Singleton states grouped by observed fresh-teacher recurrence. Counts pool states and are descriptive, not independent observations. A miss in both finite ensembles does not establish that a state cannot recur.','',
            '| Student / update / CFG | Teacher recurrence | States | Student states hit |','|---|---|---:|---:|']
    for key,groups in d['state_groups'].items():
        if not key.endswith('cfg1'):continue
        for group,r in sorted(groups.items()):
            if group.startswith('singleton'):lines.append(f"| {key} | {group} | {r['states']} | {r['student_hits']} |")
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
