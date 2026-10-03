import argparse
import json
from pathlib import Path
from native_positive_coverage import analyze_generation


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze_generation(a.runs[0])
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Native-positive decoder qualification\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='native_records'},indent=2)+'\n```\n')


if __name__=='__main__':main()
