"""Report predeclared inference-only sampler extensions and their native gates."""
import argparse,json
from pathlib import Path
from reflow_quality import native_screen
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'],screens={})
    if m['status']=='complete':
        if m.get('training_updates_executed')!=0 or not m['config'].get('evaluation_only') or len(m['scores'])!=576 or len(m['controls'])!=12:raise ValueError('incomplete inference-only evaluation')
        d.update(arm=m['config']['arm'],max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3)
        d['screens']={str(n):native_screen(m,2000,n) for n in (15,20)}
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','incomplete')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Inference-only sampler extension','',f"Status: {d['status']}; arm: {d.get('arm')}.",'','No additional training. Same existing weights, 64 tuning families and three seeds. All results retained.','', '| Steps | CA-lDDT | Delta vs original | 95% family interval | Coarse-validity delta | Native gate |','|---|---:|---:|---|---:|---|']
    for n,r in d['screens'].items():
        x=r['metrics']['ca_lddt'];v=r['metrics']['coarse_valid'];lines.append(f"| {n} | {x['candidate_mean']:.5f} | {x['difference']:+.5f} | {x['ci95']} | {v['difference']:+.5f} | {r['passed']} |")
    if 'error' in d:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
