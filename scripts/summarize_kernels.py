"""Attribute traced GPU kernels to unchanged training stages and report bottlenecks."""
import argparse, bisect, collections, json, sqlite3
from pathlib import Path
from summarize_comparison import hardware


def kernel_summary(trace, rows):
    con=sqlite3.connect(trace.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        intervals=con.execute("select start,end,text from NVTX_EVENTS where text like 'training_kernels::%' order by start").fetchall()
        expected={b['nvtx_range'] for row in rows for b in row['batches']}
        if {v[2] for v in intervals}!=expected or len(intervals)!=len(expected):raise ValueError('kernel interval coverage differs')
        if any(e is None or e<=s for s,e,_ in intervals):raise ValueError('incomplete trace ranges')
        components=con.execute("select start,end,text from NVTX_EVENTS where text like 'component::%' and text not like 'component::warmup::%' order by start").fetchall()
        starts=[v[0] for v in intervals];component_starts=[v[0] for v in components]
        totals={name:dict(kernel_ns=0,count=0,kernels=collections.Counter(),stages=collections.Counter()) for _,_,name in intervals}
        # This profiler has one GPU worker. Runtime launch timestamps attribute
        # asynchronous kernels to CPU NVTX stages without inserting GPU syncs.
        query='''select k.start,k.end,s.value,r.start from CUPTI_ACTIVITY_KIND_KERNEL k
            left join StringIds s on s.id=k.demangledName
            left join CUPTI_ACTIVITY_KIND_RUNTIME r on r.correlationId=k.correlationId
            order by k.start'''
        for begin,end,name,launch in con.execute(query):
            index=bisect.bisect_right(starts,begin)-1
            if index<0 or end>intervals[index][1]:continue
            total=totals[intervals[index][2]];duration=end-begin
            if duration<=0:raise ValueError('invalid kernel duration')
            stage='unattributed'
            if launch is not None:
                ci=bisect.bisect_right(component_starts,launch)-1
                if ci>=0 and components[ci][1] is not None and launch<=components[ci][1]:stage=components[ci][2].rsplit('::',1)[-1]
            total['kernel_ns']+=duration;total['count']+=1;total['kernels'][name or 'unknown']+=duration;total['stages'][stage]+=duration
        if any(not v['count'] for v in totals.values()):raise ValueError('a declared interval has no CUDA kernels')
        result=[]
        for row in rows:
            parts=[totals[b['nvtx_range']] for b in row['batches']];total=sum(p['kernel_ns'] for p in parts)
            if not total:raise ValueError('no CUDA kernels in a declared interval')
            kernels=collections.Counter();stages=collections.Counter()
            for part in parts:kernels.update(part['kernels']);stages.update(part['stages'])
            result.append(dict(length=row['length'],batch=row['batch'],self_condition=row['self_condition'],kernel_seconds=total/1e9,kernel_count=sum(p['count'] for p in parts),
                stage_kernel_fraction={k:v/total for k,v in stages.items()},top_kernels=[dict(name=name[:240],seconds=value/1e9,fraction=value/total) for name,value in kernels.most_common(12)]))
        return result
    finally:con.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.runs)!=1:raise ValueError('one trace expected')
    run=a.runs[0];path=run/'profile.json';d=json.loads(path.read_text()) if path.exists() else dict(status='failed',rows=[],error='No profile artifact; see scheduler exit state.')
    trace=Path(str(run)+'_nsight.sqlite')
    if d['rows']:
        d['kernel_analysis']=kernel_summary(trace,d['rows'])
        for row in d['rows']:
            prefix=f"training_kernels::L{row['length']}::sc{int(row['self_condition'])}::"
            try:row['hardware']=hardware(trace,row['batches'],prefix=prefix)
            except Exception as error:row['hardware']=dict(status='unavailable',error=str(error))
    lines=['# Training CUDA kernel diagnostic','',f"Status: {d['status']}.",'',
        'Same validated training arithmetic and batch sizes. CUDA tracing has overhead. Fractions below divide summed kernel duration, not GPU walltime or peak FLOPs. Stage attribution uses CPU launch times within explicit NVTX stages of this single-worker profiler. Unattributed kernels remain visible. No trained checkpoint or speed-promotion claim.','',
        '| Length | Self conditioning | Kernels | Forward fraction | Backward/clip fraction | Optimizer fraction |','|---:|---|---:|---:|---:|---:|']
    for row in d.get('kernel_analysis',[]):
        f=row['stage_kernel_fraction'];lines.append(f"| {row['length']} | {row['self_condition']} | {row['kernel_count']} | {f.get('forward',0):.1%} | {f.get('backward_clip',0):.1%} | {f.get('optimizer',0):.1%} |")
    lines+=['', '```json',json.dumps(d,indent=2),'```'];a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
