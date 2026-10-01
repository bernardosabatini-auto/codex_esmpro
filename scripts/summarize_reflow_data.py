"""Check full paired-noise generation coverage and measured GPU capacity."""
import argparse,json
from pathlib import Path
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='missing manifest')
    d=dict(status=m['status'])
    if m['status']=='complete':
        c=m['config'];selection=json.loads(Path(c['selection']).read_text())
        if {r['id'] for r in m['records']}!={r['id'] for r in selection['train'][c['shard']::4]} or len(m['records'])!=128 or len(m['controls'])!=4:raise ValueError('incomplete coverage')
        d.update(pairs=2048,proteins=128,controls=m['controls'],seconds=sum(r['seconds'] for r in m['batches']),peak_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3)
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','incomplete')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Paired sampler endpoints\n\n'+f"Status: {d['status']}.\n\n"+'All sixteen Gaussian seeds and 25-step CFG2 endpoints are retained per protein. These are samples from the inherited student, not new biological-state supervision.\n\n'+json.dumps({k:v for k,v in d.items() if k!='hardware'},indent=2)+'\n')


if __name__=='__main__':main()
