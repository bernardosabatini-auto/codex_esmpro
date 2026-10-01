"""Publish the completed CPU optimized-TM report without copying prediction data."""
import argparse,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];m=json.loads((run/'score.json').read_text())
    if m['status']=='complete':
        if not m.get('comparisons') or not (run/'score.md').exists():raise ValueError('missing TM analysis')
        report=(run/'score.md').read_text()
    else:report='# Optimized TM scoring\n\nStatus: '+m['status']+'\n\n'+str(m.get('error','Incomplete analysis'))+'\n'
    a.output.with_suffix('.md').write_text(report)
    a.output.with_suffix('.json').write_text(json.dumps({k:v for k,v in m.items() if k!='rows'},indent=2)+'\n')


if __name__=='__main__':main()
