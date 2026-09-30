"""Select measured safe batch sizes from an exact backward profile."""
import argparse,json
from pathlib import Path
from summarize_comparison import hardware

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if len(a.runs)!=1:raise ValueError('one run required')
 run=a.runs[0];d=json.loads((run/'profile.json').read_text());result=dict(status=d['status'],precision_controls=d['precision_controls'])
 lines=['# Backward profile','',f"Status: {d['status']}",'','Profile draws are all conditioned, late time, and self-conditioned; capacity stress rather than representative training. Adam state and optimizer arithmetic are included; learning rate zero preserves checkpoint weights.','']
 if d['status']=='complete':
  result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),d['batches']);result['selected']={}
  for length in sorted({r['length'] for r in d['rows']}):
   rows=[r for r in d['rows'] if r['length']==length and r['status']=='complete' and r['peak_reserved_bytes']<=.85*d['gpu_bytes']]
   choices=set(r['batch'] for r in rows if r['arm']=='flow')&set(r['batch'] for r in rows if r['arm']=='geometry')
   if not choices:raise ValueError('no common safe batch')
   batch=max(choices,key=lambda b:min(r['proteins_per_second'] for r in rows if r['batch']==b))
   result['selected'][str(length)]=[r for r in rows if r['batch']==batch]
  lines+=['| Length | Arm | Batch | Proteins/s | Reserved GiB |','|---:|---|---:|---:|---:|']
  for rows in result['selected'].values():
   for r in rows:lines.append(f"| {r['length']} | {r['arm']} | {r['batch']} | {r['proteins_per_second']:.2f} | {r['peak_reserved_bytes']/2**30:.2f} |")
  lines+=['',f"BF16 full-parameter gradient controls: {json.dumps(d['precision_controls'])}",'',f"Hardware: {json.dumps(result['hardware'])}"]
 else: lines.append(f"Failure: {d.get('error','unknown')}")
 a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
