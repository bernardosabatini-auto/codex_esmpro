"""Publish completed CPU ensemble analysis or its explicit failure status."""
import argparse,json,shutil
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();source=a.runs[0]/'score.json';d=json.loads(source.read_text())
    shutil.copyfile(source,a.output.with_suffix('.json'))
    if d['status']=='complete':shutil.copyfile(source.with_suffix('.md'),a.output.with_suffix('.md'))
    else:a.output.with_suffix('.md').write_text('# Ensemble state analysis\n\nStatus: '+d['status']+'.\n\n'+d.get('error','Incomplete scoring')+'\n')


if __name__=='__main__':main()
