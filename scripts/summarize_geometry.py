"""Analyze exact-coverage gradient diagnostics; never promote on surrogate loss."""
import argparse,json
from pathlib import Path
import numpy as np
from summarize_comparison import hardware

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',nargs='+',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=1: raise ValueError('one diagnostic run required')
    run=a.runs[0]; data=json.loads((run/'diagnostic.json').read_text())
    lines=['# Structural-objective diagnostic','',f"Status: {data['status']}. {len(data['rows'])}/{data['expected_rows']} gradient cases.",'',
           'Frozen current pair checkpoint; actual frozen decoder backward in strict FP32. Gradients are with respect to velocity, not head parameters. This diagnostic cannot establish an accuracy improvement.','']
    result={'status':data['status']}
    if data['status']!='complete':
        lines += [f"Failure: {data.get('error','unknown')}"]
    else:
        expected={(t['id'],time,drop) for t in data['targets'] for time in data['times'] for drop in (False,True)}
        keys=[(r['id'],r['t'],r['dropped']) for r in data['rows']]
        if set(keys)!=expected or len(keys)!=len(expected): raise ValueError('missing or duplicate gradient cases')
        result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),data['batches'])
        lines += ['| Time | Condition dropped | Loss | Median gradient / flow | Median cosine to flow |',
                  '|---:|---|---|---:|---:|']
        for t in data['times']:
            for drop in (False,True):
                rows=[r for r in data['rows'] if r['t']==t and r['dropped']==drop]
                for loss in ('legacy_independent','legacy_paired','revised'):
                    if not all(r['gradients'][loss]['finite'] for r in rows): raise ValueError('nonfinite gradient')
                    ratios=[r['gradients'][loss]['norm']/r['flow_grad_norm'] for r in rows]
                    cosines=[r['gradients'][loss]['flow_cosine'] for r in rows]
                    lines.append(f'| {t} | {drop} | {loss} | {np.median(ratios):.4f} | {np.median(cosines):.4f} |')
        late=[r for r in data['rows'] if r['t']>=.75 and not r['dropped']]
        ratio=np.median([r['gradients']['revised']['norm']/r['flow_grad_norm'] for r in late])
        result['candidate_weight_for_10pct_velocity_gradient']=float(.1/ratio)
        result['local_descent_lddt_delta']={k:float(np.mean([r['endpoint_descent'][k]['ca_lddt']-r['endpoint_before']['ca_lddt'] for r in late])) for k in late[0]['endpoint_descent']}
        result['sensitivity']=data['sensitivity']
        lines += ['',f"Candidate weight giving a median auxiliary velocity-gradient norm of 10% of flow at t≥0.75: {result['candidate_weight_for_10pct_velocity_gradient']:.5g}. Model-parameter gradient calibration remains required.",'',
                  'Mean endpoint CA-lDDT change after a diagnostic normalized velocity step (surrogate only):',
                  *[f'- {k}: {v:+.6f}' for k,v in result['local_descent_lddt_delta'].items()], '',
                  f"Peak allocated / reserved: {data['peak_allocated_bytes']/2**30:.2f} / {data['peak_reserved_bytes']/2**30:.2f} GiB.",
                  f"Hardware counters: {json.dumps(result['hardware'])}",'',
                  f"Source residue maps verified for {sum(t['residue_map'] is not None for t in data['targets'])}/{len(data['targets'])} targets; chirality uses only mapped continuous quadruples. No head weights were updated."]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__': main()
