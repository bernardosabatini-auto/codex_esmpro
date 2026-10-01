"""Compare both predeclared short samplers against initialization and noise control."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from summarize_distillation_campaign import comparison


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    values={};sources={};configs=[]
    for run in a.runs:
        path=run/'manifest.json';raw=path.read_bytes();m=json.loads(raw);c=m['config'];arm=c['arm'];sources[str(path.resolve())]=hashlib.sha256(raw).hexdigest()
        if m['status'] not in ('running','complete') or m['updates']<a.step or arm in values:raise ValueError('incomplete/duplicate arm')
        configs.append({k:v for k,v in c.items() if k!='arm'})
        selection=Path(c['selection']).read_bytes()
        if hashlib.sha256(selection).hexdigest()!=c['selection_sha256']:raise ValueError('selection changed')
        targets=json.loads(selection)['tuning'];ids=sorted(r['id'] for r in targets)
        if len(ids)!=64 or len({r['family'] for r in targets})!=64:raise ValueError('expected 64 tuning families')
        values[arm]={}
        for step,n in [(0,25),(a.step,5),(a.step,10)]:
            rows=[r for r in m['scores'] if r['step']==step and r['sampling_steps']==n]
            if len(rows)!=192 or {r['target_id'] for r in rows}!=set(ids) or any(sorted(r['sample'] for r in rows if r['target_id']==i)!=[0,1,2] for i in ids):raise ValueError('incomplete checkpoint evaluation')
            values[arm][step,n]={k:[float(np.mean([r[k] for r in rows if r['target_id']==i])) for i in ids] for k in ('ca_lddt','coarse_valid','tm_after_kabsch')}
    if set(values)!={'reflow_paired','reflow_independent'} or configs[0]!=configs[1]:raise ValueError('unmatched experiments')
    for key in values['reflow_paired'][0,25]:
        if not np.allclose(values['reflow_paired'][0,25][key],values['reflow_independent'][0,25][key],atol=2e-5,rtol=0):raise ValueError('initial predictions differ')
    results={}
    for arm in values:
        results[arm]={}
        for n in (5,10):
            metrics={base:{k:comparison(v,values[ref][step,steps][k]) for k,v in values[arm][a.step,n].items()} for base,ref,step,steps in [('initial',arm,0,25),('independent_control','reflow_independent',a.step,n)]}
            metrics['native_quality_screen_passed']=bool(metrics['initial']['ca_lddt']['ci95'][0]>-.005 and metrics['initial']['coarse_valid']['difference']>=-.01)
            results[arm][str(n)]=metrics
    d=dict(status='complete',step=a.step,source_manifest_sha256=sources,comparisons=results,scope='64 tuning families, three seeds; baseline25/CFG2 versus learned5/10-step CFG1. One training seed; state coverage and measured latency still required.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=[f'# Short-sampler tuning at {a.step} updates','',d['scope'],'','| Arm | Steps | CA-lDDT | Delta versus initial | 95% family interval | Coarse validity | Native screen |','|---|---:|---:|---:|---|---:|---|']
    for arm,steps in results.items():
        for n,r in steps.items():
            x=r['initial']['ca_lddt'];v=r['initial']['coarse_valid']
            lines.append(f"| {arm} | {n} | {x['candidate_mean']:.5f} | {x['difference']:+.5f} | [{x['ci95'][0]:+.5f}, {x['ci95'][1]:+.5f}] | {v['candidate_mean']:.5f} | {r['native_quality_screen_passed']} |")
    lines+=['','The TM diagnostic here uses Kabsch alignment. Optimized fixed-correspondence TM is scored separately. This screen alone cannot promote a sampler.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
