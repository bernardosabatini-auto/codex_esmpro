"""Per-protein repeated medians for matched sequence-to-ensemble timing."""
import argparse,json
from pathlib import Path
import numpy as np
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'],scope=m.get('scope'),summaries={})
    if m['status']=='complete':
        kinds=('student','candidate','teacher') if m['config'].get('candidate_checkpoint') else ('student','teacher')
        if len(m['rows'])!=len(kinds)*8*3*3 or len(m['controls'])!=len(kinds)*8:raise ValueError('incomplete timing or controls')
        ids=m['config']['target_ids'];d['per_target']={}
        for kind in kinds:
            d['per_target'][kind]={}
            for count in (1,8,32):
                medians={}
                for ident in ids:
                    rows=[r for r in m['rows'] if r['model']==kind and r['samples']==count and r['target_id']==ident]
                    if len(rows)!=3 or {r['repeat'] for r in rows}!={0,1,2}:raise ValueError('missing timing repeats')
                    medians[ident]=float(np.median([r['seconds'] for r in rows]))
                d['per_target'][kind][str(count)]=medians
            d['summaries'][kind]={str(count):float(np.mean(list(d['per_target'][kind][str(count)].values()))) for count in (1,8,32)}
            d['summaries'][kind]['incremental_seconds_per_sample_1_to_32']=(d['summaries'][kind]['32']-d['summaries'][kind]['1'])/31
        d['teacher_seconds_over_student']={str(count):d['summaries']['teacher'][str(count)]/d['summaries']['student'][str(count)] for count in (1,8,32)}
        if 'candidate' in kinds:d['student_seconds_over_candidate']={str(count):d['summaries']['student'][str(count)]/d['summaries']['candidate'][str(count)] for count in (1,8,32)}
        d['max_reserved_gib']={kind:max(r['peak_reserved_bytes'] for r in m['rows'] if r['model']==kind)/1024**3 for kind in kinds}
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete timing')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Matched ensemble latency','',f"Status: {d['status']}.",'',str(d['scope']),'','Eight development sequences; three timed repeats per sequence and sample count. Values average per-sequence medians. Student flow25/CFG2, decoder3. Teacher trunk3/diffusion50, at most16 samples per diffusion chunk. Neither pipeline predicts a confidence ranking in this comparison. These are resident-model latencies, not cold-start latency or maximum multi-sequence throughput.','', '| Pipeline | K1 seconds | K8 seconds | K32 seconds | Incremental seconds/sample, 1 to32 |','|---|---:|---:|---:|---:|']
    for kind,r in d['summaries'].items():lines.append('| '+kind+' | '+' | '.join(f'{v:.4f}' for v in r.values())+' |')
    if m.get('config',{}).get('candidate_checkpoint'):lines+=['',f"Candidate uses {m['config']['candidate_steps']} {m['config'].get('candidate_solver','euler')} flow intervals, CFG{m['config'].get('candidate_guidance',1)} and the same three-step decoder.",'']
    if 'error' in d:lines+=['',d['error']]
    lines+=['','This comparison does not equalize accuracy. Reference state coverage and geometry must be considered alongside cost. Student and teacher are measured sequentially on the same H200; repeat across devices before claiming a stable speed factor.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
