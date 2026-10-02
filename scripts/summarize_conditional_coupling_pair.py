"""Completion hook for the two exact registered coupling array tasks."""
import argparse,json,subprocess,sys
from pathlib import Path
from compare_conditional_coupling import main as compare_main


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();failed=[]
 for run in a.runs:
  output=a.output.parent/run.name
  subprocess.run([sys.executable,str(Path(__file__).with_name('summarize_conditional_coupling.py')),'--runs',str(run),'--output',str(output)],check=True,timeout=60)
  d=json.loads(output.with_suffix('.json').read_text())
  if d['status']!='complete':failed.append(dict(run=str(run),status=d['status'],error=d.get('error')))
 if failed:
  a.output.with_suffix('.json').write_text(json.dumps(dict(status='failed',failed=failed),indent=2)+'\n');a.output.with_suffix('.md').write_text('# Matched conditional coupling\n\nIncomplete arms; no comparison or promotion.\n\n'+json.dumps(failed,indent=2)+'\n');return
 compare_main()
if __name__=='__main__':main()
