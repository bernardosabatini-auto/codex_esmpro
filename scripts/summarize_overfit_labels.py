import argparse,json
from pathlib import Path
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    d={k:m[k] for k in ('status','audit','training_gate_passed','error') if k in m}
    if m['status']=='complete':
        if len(m['rows'])!=32 or len(m['controls'])!=8:raise ValueError('incomplete label audit')
        d['max_reserved_gib']=max(x['peak_reserved_bytes'] for x in m['batches'])/1024**3
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as e:d['hardware']=dict(status='unavailable',error=str(e))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Small-ensemble label preparation\n\n'+json.dumps({k:v for k,v in d.items() if k!='hardware'},indent=2)+'\n')

if __name__=='__main__':main()
