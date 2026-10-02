"""Strict completeness, numerical qualification and cached-stage timings."""
import argparse,itertools,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha

LAYOUTS=('single_exact','single_padded','batch8','batch32')
PRECISIONS=('fp32','tf32x3')


def analyze(m, *, candidate='tf32x3', micro_controls=True):
    precisions=('fp32',candidate)
    d=dict(status=m['status'],qualified=False,timings=[])
    if m['status']!='complete':
        d['error']=m.get('error','incomplete probe');return d
    c=m['config'];heads=[h['name'] for h in c['heads']];targets=[r['id'] for r in c['targets']]
    if len(set(heads))!=2 or len(set(targets))!=4 or m['training_updates_executed']!=0:raise ValueError('wrong probe scope')
    def complete(rows,keys,expected):
        observed=[tuple(r[k] for k in keys) for r in rows]
        if len(observed)!=len(expected) or set(observed)!=expected:raise ValueError('missing or duplicate records')
    base=list(itertools.product(heads,targets,precisions,LAYOUTS))
    complete(m['warmups'],('head','target_id','precision','layout'),set(base))
    complete(m['batches'],('head','target_id','precision','layout','repeat'),{(*v,r) for v in base for r in range(3)})
    expected={(h,t,p,l,'batching') for h,t,p,l in base if l!='single_exact'}|{(h,t,candidate,l,'arithmetic') for h,t,p,l in base}
    complete(m['controls'],('head','target_id','precision','layout','kind'),expected)
    shapes={(13,63,117):True,(128,256,256):False,(1024,1024,4096):True}
    micro=m['micro'];observed=[(tuple(r['shape']),r['precision']) for r in micro]
    if micro_controls and (len(observed)!=9 or set(observed)!=set(itertools.product(shapes,('torch_fp32','tf32','tf32x3')))):raise ValueError('missing micro controls')
    if not micro_controls and micro:raise ValueError('unexpected GEMM controls')
    if any(r['bias']!=shapes[tuple(r['shape'])] for r in micro):raise ValueError('changed micro bias')
    for rows,keys in ((micro,('relative_rms','max_abs')),(m['controls'],('ca_rmsd','ca_lddt')),(m['batches'],('seconds','peak_reserved_bytes')),(m['warmups'],('seconds',))):
        if any(not np.isfinite(r[k]) or r[k]<0 for r in rows for k in keys):raise ValueError('nonfinite or negative result')
    if any(r['seconds']<=0 for r in m['batches']+m['warmups']):raise ValueError('invalid timing')
    counts=dict(single_exact=1,single_padded=1,batch8=8,batch32=32)
    if any(r['samples']!=(1 if r['kind']=='batching' else counts[r['layout']]) for r in m['controls']):raise ValueError('wrong control sample count')
    d['micro_passed']=all(r['relative_rms']<=1e-5 for r in micro if r['precision']=='tf32x3') if micro_controls else None
    d['structural_passed']=all(r['ca_rmsd']<=.2 and r['ca_lddt']>=.99 for r in m['controls'])
    d['max_ca_rmsd']=max(r['ca_rmsd'] for r in m['controls']);d['min_pair_ca_lddt']=min(r['ca_lddt'] for r in m['controls'])
    d['max_tf32x3_relative_rms']=max((r['relative_rms'] for r in micro if r['precision']=='tf32x3'),default=None)
    d['failed_controls']=[r for r in m['controls'] if r['ca_rmsd']>.2 or r['ca_lddt']<.99]
    for h,t,l in itertools.product(heads,targets,LAYOUTS):
        times={p:float(np.median([r['seconds'] for r in m['batches'] if (r['head'],r['target_id'],r['layout'],r['precision'])==(h,t,l,p)])) for p in precisions}
        d['timings'].append(dict(head=h,target_id=t,layout=l,**times,speed_ratio=times['fp32']/times[candidate]))
    d['batch32_speed_ratio']=sum(r['fp32'] for r in d['timings'] if r['layout']=='batch32')/sum(r[candidate] for r in d['timings'] if r['layout']=='batch32')
    d['warmup_seconds']={p:sum(r['seconds'] for r in m['warmups'] if r['precision']==p) for p in precisions}
    d['peak_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
    d['qualified']=bool((not micro_controls or d['micro_passed']) and d['structural_passed'] and d['batch32_speed_ratio']>1)
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json'
    m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']=='complete':
        for field in ('selection','protocol'):
            if sha(m['config'][field])!=m['config'][field+'_sha256']:raise ValueError('changed '+field)
    d=analyze(m)
    try:
        from summarize_comparison import hardware
        d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m.get('batches',[]))
    except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    lines=['# Scoped TF32x3 numerical and stage-speed probe','',f"Status: {d['status']}; qualifies for broader validation: {d['qualified']}.",'','Four longest tuning-bucket proteins, original CFG2 and balanced500 CFG1, Euler25/decoder3. Only DiT MLP and QKV/output projections change arithmetic. This is not IEEE equality, full-panel accuracy, or an end-to-end speed measurement. All micro and structural controls must pass before follow-up.']
    if d['status']=='complete':
        lines += ['',f"Worst paired CA-RMSD: {d['max_ca_rmsd']:.6f} A; minimum pair CA-lDDT: {d['min_pair_ca_lddt']:.6f}. Maximum TF32x3 micro relative-RMS error: {d['max_tf32x3_relative_rms']:.3g}.",f"Batch32 ratio of summed per-target median times: {d['batch32_speed_ratio']:.4f}. Warmup totals (including first compilation): {d['warmup_seconds']}. Peak reserved: {d['peak_reserved_gib']:.2f} GiB.",'','| Head | Target | Layout | FP32 seconds | TF32x3 seconds | Speed ratio |','|---|---|---|---:|---:|---:|']
        for r in d['timings']:lines.append(f"| {r['head']} | {r['target_id']} | {r['layout']} | {r['fp32']:.4f} | {r['tf32x3']:.4f} | {r['speed_ratio']:.3f} |")
        lines += ['',f"Failed structural controls: {json.dumps(d['failed_controls'])}"]
    else:lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
