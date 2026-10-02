"""Report controlled training-only feature cache completion."""
import argparse,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs=1,type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest')
    d={k:v for k,v in m.items() if k!='config'}
    lines=['# Frozen teacher-summary training cache','',f"Status: {m['status']}; qualified: {m.get('qualified',False)}.",'','The unchanged reliable32 training families only. Equal256D projected-final and pretrained-mixture inputs; no student learning or native/external scoring.']
    if m['status']=='complete':
        if len(m['rows'])!=32 or len(m['controls'])!=4 or not m['qualified']:raise ValueError('incomplete cache')
        lines+=['',f"32 historical final embedding controls and4 full hidden-state summary controls pass. Peak {m['peak_reserved_gib']:.3f}GiB; worker {m['elapsed_seconds']:.2f}s."]
    else:lines+=['',m.get('error','incomplete')]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
