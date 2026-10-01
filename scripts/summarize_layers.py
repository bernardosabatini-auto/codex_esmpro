"""Summarize bounded ESMC extraction profiling without implying layer quality."""
import argparse,json
from pathlib import Path
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='No manifest')
    result=dict(status=m['status'],scope='Extraction implementation and capacity only; no earlier-layer accuracy conclusion')
    if m['status']=='complete':
        if m['completed_targets']!=16 or len(m['controls'])!=4 or len(m['batches'])!=12 or any(c['final_layer_max_abs']>1e-6 for c in m['controls']):raise ValueError('incomplete extraction controls')
        result['buckets']={str(length):dict(batch=rows[0]['batch'],sequences_per_second=sum(r['batch'] for r in rows)/sum(r['seconds'] for r in rows),peak_reserved_gib=max(r['peak_reserved_bytes'] for r in rows)/2**30) for length in (128,256,384,512) if (rows:=[r for r in m['batches'] if r['length']==length])}
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','incomplete')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Selected ESMC layers: extraction calibration','',f"Status: {result['status']}.",'','Layers 20/40/60 are post-block residual streams; layer 80 includes final normalization and is checked against the existing final-layer extractor. Repeated inputs measure capacity, not independent targets or earlier-layer predictive value.','', '| Length | Batch | Sequences/s | Reserved GiB |','|---:|---:|---:|---:|']
    for length,row in result.get('buckets',{}).items():lines.append(f"| {length} | {row['batch']} | {row['sequences_per_second']:.3f} | {row['peak_reserved_gib']:.2f} |")
    if 'error' in result:lines+=['',result['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
