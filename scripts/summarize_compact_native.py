"""Full-panel noninferiority with frozen-output and batching agreement."""
import argparse,itertools,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change


def analyze(m):
    c=m['config']
    for key in ('selection','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    p=json.loads(Path(c['protocol']).read_text());families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']};heads=p['heads'];modes=p['modes']
    if len(families)!=64 or len(set(families.values()))!=64 or heads!=['original','aligned_teacher_balanced'] or modes!=['fp32','compact'] or [h['name'] for h in c['heads']]!=heads or m['training_updates_executed']!=0:raise ValueError('wrong scope')
    def complete(rows,keys,expected):
        seen=[tuple(r[k] for k in keys) for r in rows]
        if len(seen)!=len(expected) or set(seen)!=expected:raise ValueError('missing or duplicate records')
    expected=set(itertools.product(heads,modes,families,range(3)))
    for key in ('scores','agreement'):complete(m[key],('head','mode','target_id','sample'),expected)
    complete(m['controls'],('head','mode','length'),set(itertools.product(heads,modes,(128,256,384,512))))
    complete(m['batches'],('head','mode','target_id'),set(itertools.product(heads,modes,families)))
    if any(not np.isfinite(r[k]) for r in m['controls']+m['agreement'] for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in m['controls']+m['agreement']):raise ValueError('failed agreement controls')
    if any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in m['scores'] for k in ('ca_lddt','coarse_valid')):raise ValueError('invalid quality score')
    if any(not np.isfinite(r['seconds']) or r['seconds']<=0 for r in m['batches']):raise ValueError('invalid timing')
    rows=m['scores'];values={(h,mode):{k:{i:float(np.mean([r[k] for r in rows if (r['head'],r['mode'],r['target_id'])==(h,mode,i)])) for i in families} for k in ('ca_lddt','coarse_valid')} for h,mode in itertools.product(heads,modes)}
    def compare(a,b):return {k:paired_change(values[a][k],values[b][k],families=families) for k in ('ca_lddt','coarse_valid')}
    def passed(metrics):return bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01)
    d=dict(summaries={},implementation={})
    for h,mode in itertools.product(heads,modes):
        metrics=compare((h,mode),('original','fp32'));d['summaries'][h+'_'+mode]=dict(metrics=metrics,quality_passed=passed(metrics))
    for h in heads:
        metrics=compare((h,'compact'),(h,'fp32'));d['implementation'][h]=dict(metrics=metrics,quality_passed=passed(metrics))
    d['max_frozen_rmsd']=max(r['ca_rmsd'] for r in m['agreement'] if r['mode']=='fp32');d['max_implementation_rmsd']=max(r['ca_rmsd'] for r in m['agreement'] if r['mode']=='compact')
    d['qualified_heads']=[h for h in heads if d['implementation'][h]['quality_passed'] and d['summaries'][h+'_compact']['quality_passed']]
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':
        d.update(analyze(m));d['manifest_sha256']=sha(path)
        try:
            from summarize_comparison import hardware
            d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete screen')
    lines=['# Compact conditioning: full tuning-panel validation','',f"Status: {d['status']}.",'','64 tuning families, three paired samples, two frozen checkpoints, expanded/compact strict FP32. Every expanded output is compared with its frozen source; every compact output with its same-device expanded counterpart. All768 scores and768 agreement controls plus16 batching controls required. Unadjusted family intervals; invalid samples retained. No locked tests or end-to-end speed claim.','','| Pipeline | CA-lDDT | Delta vs fresh original |95% interval | Valid | Validity delta | Qualified |','|---|---:|---:|---|---:|---:|---|']
    for name,r in d.get('summaries',{}).items():
        ca=r['metrics']['ca_lddt'];v=r['metrics']['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['quality_passed']} |")
    for h,r in d.get('implementation',{}).items():lines+=['',f"{h}, compact minus expanded: CA-lDDT {r['metrics']['ca_lddt']['difference']:+.6f},95% interval {r['metrics']['ca_lddt']['ci95']}; validity {r['metrics']['coarse_valid']['difference']:+.6f}; noninferior {r['quality_passed']}."]
    if 'error' in d:lines+=['',d['error']]
    else:lines+=['',f"Maximum frozen-output RMSD {d['max_frozen_rmsd']:.6f}A; implementation RMSD {d['max_implementation_rmsd']:.6f}A. Qualified heads: {d['qualified_heads']}.",'Passing permits separate48-family ensemble assessment and matched resident sequence timing, not automatic adoption.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
