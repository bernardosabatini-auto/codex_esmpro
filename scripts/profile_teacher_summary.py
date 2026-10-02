"""Bounded numerical and latency screen for a frozen pretrained layer mixture."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.embedding import FinalESMC
from latentfold.precision import inference_precision
from teacher_summary import load_adapter,StreamedSummary,full_summary
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def hooks(model):return {name:tuple(module._forward_hooks) for name,module in model.named_modules()}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','panel','source_latency_config','embedding_cache'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    recipe=json.loads(Path(c['protocol']).read_text());allrows={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']};rows=[allrows[i] for i in c['target_ids']]
    if len(rows)!=8 or len({r['family'] for r in rows})!=8:raise ValueError('wrong fixed panel')
    with h5py.File(c['embedding_cache']) as h:cached={r['query_id']:h[r['query_id']]['80'][:] for r in rows}
    adapter,identity=load_adapter(a.source/'data/esmfold2_fast')
    if identity!=c['adapter_tensor_sha256']:raise ValueError('teacher projection changed')
    a.output.mkdir(parents=True,exist_ok=False);torch.cuda.set_device(0);torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],rows=[],batches=[],adapter_tensor_sha256=identity);atomic_json(a.output/'manifest.json',m)
    try:
        m['gpu']=torch.cuda.get_device_name(0)
        if 'RTX PRO 6000' not in m['gpu']:raise ValueError('RTX profile required')
        e=FinalESMC(a.source/'data/esmc6b',precision='fp32');adapter.cuda();streamed=StreamedSummary(e,adapter);torch.cuda.synchronize();m['loading_seconds']=time.monotonic()-start;telemetry=Telemetry(a.output,True)
        def control(sequences,length,label,identifiers):
            final,reference=full_summary(e,sequences,length,adapter);before=hooks(e.model);actual_final,actual=streamed(sequences,length)
            delta=actual-reference;mask=torch.arange(length,device='cuda')[None]<torch.tensor([len(s) for s in sequences],device='cuda')[:,None]
            r=dict(label=label,batch=len(sequences),length=length,summary_rmse=float(delta[mask].square().mean().sqrt()),summary_max_abs=float(delta[mask].abs().max()),final_max_abs=float((final-actual_final).abs().max()),padding_exact_zero=bool(torch.count_nonzero(actual[~mask])==0),hooks_restored=hooks(e.model)==before and not adapter.single_to_pair._forward_pre_hooks)
            errors=np.concatenate([(actual_final[i,:len(s)].cpu().numpy()-cached[ident]).ravel() for i,(s,ident) in enumerate(zip(sequences,identifiers))])
            r.update(cached_final_rmse=float(np.sqrt(np.mean(errors**2))),cached_final_max_abs=float(np.abs(errors).max()))
            tol=recipe['controls'];r['passed']=r['summary_rmse']<=tol['max_summary_rmse'] and r['summary_max_abs']<=tol['max_summary_abs'] and r['final_max_abs']<=tol['max_final_embedding_abs'] and r['cached_final_rmse']<=tol['max_cached_embedding_rmse'] and r['cached_final_max_abs']<=tol['max_cached_embedding_abs'] and r['padding_exact_zero'] and r['hooks_restored'];m['controls'].append(r)
            if not r['passed']:raise ValueError('teacher summary control failed')
            return actual_final,actual
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'features.h5','x') as out:
            # Largest mixed batch first establishes resource headroom.
            mixed=sorted(rows,key=lambda r:(r['length'],r['query_id']))
            control([mixed[0]['sequence'],mixed[-1]['sequence']],512,'mixed_length_batch2',[mixed[0]['query_id'],mixed[-1]['query_id']])
            m['control_peak_reserved_bytes']=torch.cuda.max_memory_reserved()
            if m['control_peak_reserved_bytes']>80*1024**3:raise MemoryError('feature reference exceeds80GiB')
            torch.cuda.empty_cache()
            for row in rows:
                if time.monotonic()-start>480:raise TimeoutError('feature profile work cap')
                n=row['length'];length=next(b for b in (128,256,384,512) if n<=b);sequence=[row['sequence']]
                final,summary=control(sequence,length,row['query_id'],[row['query_id']]);g=out.create_group(row['query_id']);g.create_dataset('80',data=final[0,:n].cpu().numpy());g.create_dataset('teacher_summary',data=summary[0,:n].cpu().numpy());del final,summary
                e(sequence,length);streamed(sequence,length);torch.cuda.synchronize()
                for repeat in range(3):
                    for kind in (('vanilla','streamed') if repeat%2==0 else ('streamed','vanilla')):
                        name=f"collect::teacher_summary::{row['query_id']}::{repeat}::{kind}";torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                        try:
                            value=streamed(sequence,length) if kind=='streamed' else e(sequence,length)
                            torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['rows'].append(dict(target_id=row['query_id'],family=row['family'],repeat=repeat,kind=kind,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()));m['batches'].append(dict(nvtx_range=name));del value
                atomic_json(a.output/'manifest.json',m);print(row['query_id'],'controlled',flush=True)
        if len(m['controls'])!=9 or len(m['rows'])!=48:raise ValueError('incomplete extraction probe')
        m['qualified']=max([m['control_peak_reserved_bytes']]+[r['peak_reserved_bytes'] for r in m['rows']])<=80*1024**3;m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
