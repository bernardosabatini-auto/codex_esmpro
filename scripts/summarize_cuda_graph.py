"""Report graph feasibility and paired cached-generation latency separately."""
import argparse,json
from pathlib import Path
import numpy as np
from summarize_ensemble_latency import speed_ratio


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'],qualified=False)
    if m['status']=='complete':
        ids=m['config']['target_ids'];expected={(i,k,r) for i in ids for k in (1,32) for r in range(3)}
        if len(m['controls'])!=len(expected) or {(r['target_id'],r['samples'],r['repeat']) for r in m['controls']}!=expected or any(not r['passed'] for r in m['controls']):raise ValueError('incomplete or failed controls')
        if len(m['rows'])!=2*len(expected) or {(r['target_id'],r['samples'],r['repeat'],r['kind']) for r in m['rows']}!={(*t,k) for t in expected for k in ('eager','captured')}:raise ValueError('incomplete timing')
        d.update(qualified=m['qualified'],gpu=m['gpu'],controls=m['controls'],construction=m['construction'],max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['rows']+m['construction'])/1024**3,comparisons={})
        for k in (1,32):
            values={kind:{i:float(np.median([r['seconds'] for r in m['rows'] if (r['target_id'],r['samples'],r['kind'])==(i,k,kind)])) for i in ids} for kind in ('eager','captured')}
            d['comparisons'][str(k)]=dict(eager_mean=float(np.mean(list(values['eager'].values()))),captured_mean=float(np.mean(list(values['captured'].values()))),**speed_ratio(values['eager'],values['captured']))
        d['full_pipeline_followup_justified']=d['qualified'] and any(r['reference_seconds_over_candidate']>=1.1 for r in d['comparisons'].values())
    else:d['error']=m.get('error','incomplete')
    lines=['# CUDA graph sampler probe','',f"Status: {d['status']}; numerical/resource qualified: {d['qualified']}.",'','Same compact balanced500 checkpoint, FP32 CFG1/Euler25/AE3;8 development families,3 paired noise repeats,K1/32. GPU-cached embeddings/noise to CPU backbone only. Graph capture/loading/ESMC/disk excluded. All replay copies, validation and cloning included. No full sequence-to-backbone speed claim.']
    if d['status']=='complete':
        lines+=['','| Samples | Eager s | Captured s | Ratio | Family95% interval |','|---|---:|---:|---:|---|']
        for k,r in d['comparisons'].items():lines.append(f"| {k} | {r['eager_mean']:.4f} | {r['captured_mean']:.4f} | {r['reference_seconds_over_candidate']:.4f} | {r['ci95']} |")
        lines+=['',f"Peak reserved{d['max_reserved_gib']:.3f}GiB. Graph construction seconds by(bucket,K): "+str([(r['length'],r['samples'],round(r['seconds'],3)) for r in d['construction']]),'',f"Separate full-pipeline follow-up justified: {d['full_pipeline_followup_justified']}."]
    else:lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
