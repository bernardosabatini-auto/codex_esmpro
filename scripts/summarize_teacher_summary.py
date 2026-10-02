"""Report frozen ESM mixture extraction, not downstream accuracy."""
import argparse,json
from pathlib import Path
import numpy as np
from summarize_ensemble_latency import speed_ratio


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'],qualified=False)
    if m['status']=='complete':
        ids=m['config']['target_ids'];expected={(i,r,k) for i in ids for r in range(3) for k in ('vanilla','streamed')}
        if len(m['controls'])!=9 or {r['label'] for r in m['controls']}!=set(ids)|{'mixed_length_batch2'} or any(not r['passed'] for r in m['controls']) or len(m['rows'])!=len(expected) or {(r['target_id'],r['repeat'],r['kind']) for r in m['rows']}!=expected:raise ValueError('incomplete or failed feature controls')
        values={k:{i:float(np.median([r['seconds'] for r in m['rows'] if (r['target_id'],r['kind'])==(i,k)])) for i in ids} for k in ('vanilla','streamed')}
        ratio=speed_ratio(values['streamed'],values['vanilla'])
        d.update(qualified=m['qualified'] and ratio['reference_seconds_over_candidate']<=1.15,gpu=m['gpu'],controls=m['controls'],per_target=values,streamed_over_vanilla=ratio,means={k:float(np.mean(list(v.values()))) for k,v in values.items()},max_reserved_gib=max([m['control_peak_reserved_bytes']]+[r['peak_reserved_bytes'] for r in m['rows']])/1024**3,loading_seconds=m['loading_seconds'],elapsed_seconds=m['elapsed_seconds'])
    else:d['error']=m.get('error','incomplete')
    lines=['# Frozen teacher ESM summary extraction','',f"Status: {d['status']}; numerical/resource/overhead qualification: {d['qualified']}.",'','One pretrained81-layer mixture, learned normalization and256-dimensional projection; no teacher folding trunk or diffusion. Existing final ESMC embedding retained. Nine controls include all8 fixed development sequences and a mixed-length batch. This does not establish predictive usefulness or justify long training.']
    if d['status']=='complete':
        lines+=['',f"Vanilla/streamed extraction means of3-repeat sequence medians: {d['means']['vanilla']:.5f}/{d['means']['streamed']:.5f}s; streamed/vanilla ratio{d['streamed_over_vanilla']['reference_seconds_over_candidate']:.5f}, family95% interval{d['streamed_over_vanilla']['ci95']}.",'',f"Peak including full-state controls{d['max_reserved_gib']:.3f}GiB; loading{d['loading_seconds']:.2f}s; worker{d['elapsed_seconds']:.2f}s. Timings include tokenization and GPU work, exclude loading/reference controls/disk; GPU feature outputs remain resident."]
        for r in d['controls']:lines+=['',f"{r['label']}: summaryRMSE{r['summary_rmse']:.6g},max{r['summary_max_abs']:.6g}; finalembeddingmax{r['final_max_abs']:.6g}; padding/hooks {r['padding_exact_zero']}/{r['hooks_restored']}."]
    else:lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
