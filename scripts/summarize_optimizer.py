"""Report the bounded AdamW kernel experiment without automatic adoption."""
import argparse,json
from pathlib import Path
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=1:raise ValueError('one optimizer profile required')
    run=a.runs[0];path=run/'profile.json';d=json.loads(path.read_text()) if path.exists() else dict(status='failed',rows=[],controls=[],error='No profile artifact; see registered scheduler exit state.')
    lines=['# AdamW implementation profile','',f"Status: {d['status']}. All-block recomputation and scientific batch sizes are retained.",'',
        '| Length | AdamW | Batch | Proteins/s | Reserved GiB | SM issue % |','|---:|---|---:|---:|---:|---:|']
    for row in d['rows']:
        prefix=f"optimizer_profile::{row['length']}::{row['policy']}::{row['batch']}::"
        try:
            row['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),row['batches'],prefix=prefix)
            issue=f"{row['hardware']['collection_mean_percent']['SM Issue [Throughput %]']:.1f}"
        except Exception as error:row['hardware']=dict(status='unavailable',error=str(error));issue='unavailable'
        lines.append(f"| {row['length']} | {row['policy']} | {row['batch']} | {row['proteins_per_second']:.2f} | {row['peak_reserved_bytes']/2**30:.1f} | {issue} |")
    lines+=['','Optimizer arithmetic controls do not establish training-trajectory equivalence. Any adoption requires an actual matched trajectory test. SM issue is not percent of peak FLOPs.','', '```json',json.dumps(d,indent=2),'```']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
