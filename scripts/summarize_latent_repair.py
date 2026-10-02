"""Report fixed training-only latent repair feasibility, including failures."""
import argparse,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'],qualified=False)
    if m['status']=='complete':
        if len(m['sources'])!=2 or any(len(s['targets'])!=122 or len(s['controls'])!=4 for s in m['sources']):raise ValueError('incomplete fixed screen')
        d.update(qualified=m['qualified'],sources=m['sources'],gpu=m['gpu'],elapsed_seconds=m['elapsed_seconds'],max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3,timing=m['timing'])
    else:d['error']=m.get('error','incomplete')
    lines=['# Conditional latent repair: training feasibility','',f"Status: {d['status']}; both-seed qualification: {d['qualified']}.",'','All122 training families ×32 saved samples at each of two seeds. Only invalid outputs undergo bounded12-step latent optimization with the same decoder noise. Valid outputs and failed repairs remain exactly unchanged. This does not qualify raw models, native accuracy, external diversity, or physical plausibility.']
    if d['status']=='complete':
        lines+=['','| Training job | Invalid | Repaired | Fraction | Mean s/32 | Max s/32 | Feasible |','|---|---:|---:|---:|---:|---:|---|']
        for s in d['sources']:lines.append(f"| {s['job_id']} | {s['invalid']} | {s['repaired']} | {s['repaired_fraction']:.4f} | {s['mean_seconds_per32']:.4f} | {s['max_seconds_per32']:.4f} | {s['feasible']} |")
        lines+=['',f"GPU: {d['gpu']}; peak reserved{d['max_reserved_gib']:.3f}GiB; elapsed{d['elapsed_seconds']:.2f}s.",'',d['timing']]
    else:lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
