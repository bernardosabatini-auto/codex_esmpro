"""Full probe controls and memory changes for compact conditioning."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from summarize_tensor_precision import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']=='complete':
        for key in ('selection','protocol'):
            if sha(m['config'][key])!=m['config'][key+'_sha256']:raise ValueError('changed '+key)
    d=analyze(m,candidate='compact',micro_controls=False)
    if m['status']=='complete':
        for row in d['timings']:
            for mode in ('fp32','compact'):
                rows=[r for r in m['batches'] if (r['head'],r['target_id'],r['layout'],r['precision'])==(row['head'],row['target_id'],row['layout'],mode)]
                if any(not np.isfinite(r['peak_allocated_bytes']) or r['peak_allocated_bytes']<=0 for r in rows):raise ValueError('invalid allocated memory')
                row[mode+'_allocated_gib']=max(r['peak_allocated_bytes'] for r in rows)/1024**3
                row[mode+'_reserved_gib']=max(r['peak_reserved_bytes'] for r in rows)/1024**3
    try:
        from summarize_comparison import hardware
        d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m.get('batches',[]))
    except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    lines=['# Compact single-sequence conditioning probe','',f"Status: {d['status']}; qualifies for broader validation: {d['qualified']}.",'','Original CFG2 and balanced500 CFG1, four longest tuning-bucket proteins, exact/padded single and batches8/32. Both paths retain strict FP32. Three measured repeats after one warmup per layout; allocator cache cleared between layouts. Flow, decoder and output transfer included, ESMC excluded. All80 structural controls required. This is not full-panel accuracy or an end-to-end speedup.']
    if d['status']=='complete':
        lines+=['',f"Worst CA-RMSD {d['max_ca_rmsd']:.6f}A; minimum pair CA-lDDT {d['min_pair_ca_lddt']:.6f}. Batch32 ratio of summed medians {d['batch32_speed_ratio']:.4f}.",'','| Head | Target | Layout | Expanded seconds | Compact seconds | Speed ratio | Expanded allocated GiB | Compact allocated GiB |','|---|---|---|---:|---:|---:|---:|---:|']
        for r in d['timings']:lines.append(f"| {r['head']} | {r['target_id']} | {r['layout']} | {r['fp32']:.4f} | {r['compact']:.4f} | {r['speed_ratio']:.3f} | {r['fp32_allocated_gib']:.2f} | {r['compact_allocated_gib']:.2f} |")
        lines+=['',f"Failed controls: {json.dumps(d['failed_controls'])}"]
    else:lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
