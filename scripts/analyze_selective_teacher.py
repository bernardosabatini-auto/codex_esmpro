"""Frozen reference-free fallback policies evaluated on existing development outputs."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from scipy.stats import pearsonr
from prepare_overfit import sha


def correlation(x,y):
    if len(x)<3 or np.std(x)==0 or np.std(y)==0:return None
    return float(pearsonr(x,y).statistic)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/selective_teacher_protocol.json';recipe=json.loads(protocol.read_text());choices_path=root/recipe['choices'];choices=json.loads(choices_path.read_text());run=root/recipe['student_run'];teacher=root/recipe['teacher_run'];sm=json.loads((run/'manifest.json').read_text());tm=json.loads((teacher/'manifest.json').read_text())
    if sm['status']!='complete' or tm['status']!='complete' or sha(run/'manifest.json')!=choices['manifest_sha256'] or sha(run/'predictions.h5')!=choices['predictions_sha256']:raise ValueError('Invalid source predictions')
    ids=sorted(choices['choices']);spread={};lengths={}
    if len(ids)!=626 or set(ids)!=set(sm['config']['target_ids']) or set(ids)!=set(tm['target_ids']):raise ValueError('Wrong target coverage')
    for ident in ids:
        r=choices['choices'][ident];matrix=np.asarray(r['pairwise'])
        if matrix.shape!=(3,3) or not np.isfinite(matrix).all() or np.any((matrix<0)|(matrix>1)):raise ValueError('Invalid pairwise agreement')
        spread[ident]=float(1-matrix[~np.eye(3,dtype=bool)].mean())
    with h5py.File(run/'predictions.h5') as f:
        for group in f['steps25_cfg2'].values():lengths[group.attrs['target_id']]=group['0']['ca'].shape[0]
    if set(lengths)!=set(ids):raise ValueError('Missing lengths')
    count=math.ceil(.25*len(ids));selected=set(sorted(ids,key=lambda i:(-spread[i],i))[:count]);longest=set(sorted(ids,key=lambda i:(-lengths[i],i))[:count]);frozen=dict(protocol_sha256=sha(protocol),choices_sha256=sha(choices_path),disagreement=sorted(selected),longest=sorted(longest),count=count)
    selection=a.output.parent.parent/'runs/selective_teacher_choices.json'
    if selection.exists() and json.loads(selection.read_text())!=frozen:raise ValueError('Existing frozen choices differ')
    selection.write_text(json.dumps(frozen,indent=2)+'\n')
    # No reference score has been opened when the policies above are frozen.
    ss=json.loads((run/'scores.json').read_text());ts=json.loads((teacher/'scores.json').read_text());clusters_path=root/recipe['clusters'];clusters=json.loads(clusters_path.read_text())['clusters']
    for data,setting in [(ss,'steps25_cfg2'),(ts,'esmfold2_steps50_loops3')]:
        records=[r for r in data['records'] if r['setting']==setting]
        if len(records)!=1878 or {(r['target_id'],r['sample']) for r in records}!={(i,k) for i in ids for k in range(3)}:raise ValueError('Missing/duplicate source samples')
    students={};teachers={}
    for r in ss['records']:
        if r['setting']=='steps25_cfg2' and r['sample']==choices['choices'][r['target_id']]['sample']:students[r['target_id']]=r
    for r in ts['records']:
        if r['sample']==0:teachers[r['target_id']]=r
    if set(students)!=set(ids) or set(teachers)!=set(ids):raise ValueError('Incomplete score coverage')
    if ss['usalign']!=ts['usalign']:raise ValueError('Different score implementations')
    names=sorted({clusters[i] for i in ids});members=[np.array([j for j,i in enumerate(ids) if clusters[i]==name]) for name in names];rng=np.random.default_rng(2026100216);ix=rng.integers(0,len(names),(10000,len(names)));sizes=np.array([len(v) for v in members]);denom=sizes[ix].sum(1)
    def ci(values):
        sums=np.array([values[v].sum() for v in members]);return np.quantile(sums[ix].sum(1)/denom,[.025,.975]).tolist()
    use=np.array([i in selected for i in ids]);use_long=np.array([i in longest for i in ids]);x=np.array([spread[i] for i in ids]);length=np.array([lengths[i] for i in ids]);cov=np.stack([np.ones(len(ids)),np.log(length),np.log(length)**2],axis=1)
    partial=lambda v:v-cov@np.linalg.lstsq(cov,v,rcond=None)[0]
    results={}
    for metric in ('tm_fixed_reference','ca_lddt'):
        base=np.array([students[i][metric] for i in ids]);full=np.array([teachers[i][metric] for i in ids]);benefit=full-base
        if not np.isfinite(base).all() or not np.isfinite(full).all():raise ValueError('Nonfinite scores')
        policies={'student':base,'disagreement25':np.where(use,full,base),'length25':np.where(use_long,full,base),'random25_expectation':base+count/len(ids)*benefit,'teacher':full};statistics={}
        for name,y in policies.items():statistics[name]=dict(mean=float(y.mean()),delta_vs_student=float((y-base).mean()),delta_ci=ci(y-base))
        for name in ('length25','random25_expectation'):statistics['disagreement_vs_'+name]=dict(delta=float((policies['disagreement25']-policies[name]).mean()),ci=ci(policies['disagreement25']-policies[name]))
        corr={}
        for name,keep in [('all',np.ones(len(ids),dtype=bool)),('short',length<=256),('long',length>256)]:corr[name]=dict(n=int(keep.sum()),spread_vs_student_error=correlation(x[keep],1-base[keep]),spread_vs_teacher_benefit=correlation(x[keep],benefit[keep]))
        corr['length_adjusted']=dict(spread_vs_student_error=correlation(partial(x),partial(1-base)),spread_vs_teacher_benefit=correlation(partial(x),partial(benefit)))
        results[metric]=dict(policies=statistics,correlations=corr)
    d=dict(status='complete',targets=626,clusters=len(names),teacher_calls=count,teacher_fraction=count/626,selection_sha256=sha(selection),student_scores_sha256=sha(run/'scores.json'),teacher_scores_sha256=sha(teacher/'scores.json'),results=results);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Reference-free teacher fallback diagnostic','','All626 repeatedly used development targets; no held-out claim. Student is the existing3sample medoid, teacher is fixed sample0.157teacher calls for both disagreement and length policies, frozen before reference scores. No new GPU inference and no end-to-end speed claim.','', '| Policy | TM | Change vs student [95%cluster CI] |','|---|---:|---|']
    for name,r in results['tm_fixed_reference']['policies'].items():
        if 'mean' in r:lines.append(f"| {name} | {r['mean']:.5f} | {r['delta_vs_student']:+.5f} {r['delta_ci']} |")
    lines+=['','Disagreement relative to equal-budget alternatives:']
    for name in ('length25','random25_expectation'):lines.append(str(results['tm_fixed_reference']['policies']['disagreement_vs_'+name]))
    lines+=['','TM-based correlations:',json.dumps(results['tm_fixed_reference']['correlations'],indent=2),'','A correlation with student error is not calibration or proof of teacher benefit. Cost must include all3student samples plus selected teacher calls. No threshold tuning, oracle sample choice, independent tests or retraining.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
