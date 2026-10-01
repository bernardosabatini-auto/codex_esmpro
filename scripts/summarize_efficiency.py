"""Report measured recomputation savings without changing scientific recipes."""
import argparse,json
from pathlib import Path
from summarize_comparison import hardware

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=1:raise ValueError('one profile required')
    run=a.runs[0];d=json.loads((run/'profile.json').read_text());lines=['# Activation recomputation profile','',d['scope'],'',f"Status: {d['status']}",'',
        '| Padded length | Policy | Batch | Proteins/s | Reserved GiB | SM issue % |', '|---:|---|---:|---:|---:|---:|']
    for row in d['rows']:
        if row['status']!='complete':lines.append(f"| {row['length']} | {row['policy']} | {row['batch']} | out of memory | — | — |");continue
        try:
            row['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),row['batches'],prefix='checkpoint_profile::')
            issue=f"{row['hardware']['collection_mean_percent']['SM Issue [Throughput %]']:.1f}"
        except Exception as error:row['hardware']=dict(status='unavailable',error=str(error));issue='unavailable'
        lines.append(f"| {row['length']} | {row['policy']} | {row['batch']} | {row['proteins_per_second']:.2f} | {row['peak_reserved_bytes']/2**30:.1f} | {issue} |")
    if d.get('error'):lines+=['',d['error']]
    lines+=['','Only compare unchanged batch sizes for direct adoption into matched training. Half-batch measurements are capacity diagnostics. Recheck actual training trajectory before using any faster policy for new scientific comparisons. SM issue is not percent of peak FLOPs.','', '```json',json.dumps(d['controls'],indent=2),'```']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
