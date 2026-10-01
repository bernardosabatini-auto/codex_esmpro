"""Bounded CUDA kernel trace of the unchanged validated training implementation."""
import argparse, contextlib, gc, json, time
from pathlib import Path
import torch
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig
from latentfold.training import objective, controlled_backward
from latentfold.precision import inference_precision
from profile_training import make_batch
from profile_gpu import Telemetry, atomic_json


@contextlib.contextmanager
def span(label):
    torch.cuda.nvtx.range_push(label)
    try:yield
    finally:torch.cuda.nvtx.range_pop()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--targets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.manual_seed(0);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    torch.set_float32_matmul_precision('highest');torch.backends.cudnn.allow_tf32=False
    start=time.monotonic();telemetry=None;report=dict(status='running',rows=[],scope='Unchanged FP16 forward, all-block recomputation, controlled backward with scale 128 and clipping, single-tensor AdamW and EMA. Zero LR keeps weights fixed. Repeated profile inputs are not independent proteins. CUDA tracing adds overhead; no speed-promotion claim.')
    try:
        model,_=load_legacy(a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt',trusted_pickle=True);model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
        parameters=list(model.parameters());optimizer=torch.optim.AdamW(parameters,lr=0.,weight_decay=.01,betas=(.9,.999),foreach=False)
        ema=[p.detach().clone() for p in parameters];targets=json.loads(a.targets.read_text())['targets'];telemetry=Telemetry(a.output,True)
        def step(batch,self_condition,seed,label):
            with span('component::'+label+'::forward'):
                optimizer.zero_grad(set_to_none=True);generator=torch.Generator(device='cuda').manual_seed(seed)
                with inference_precision('fp16'):
                    loss,_,_=objective(model,decoder,batch,FlowConfig(self_condition_probability=float(self_condition)),generator=generator,return_parts=True)
            with span('component::'+label+'::backward_clip'):
                controlled_backward(model,loss,None,weight=0,loss_scale=128.)
                torch.nn.utils.clip_grad_norm_(parameters,1.,error_if_nonfinite=True)
            with span('component::'+label+'::optimizer'):optimizer.step()
            with span('component::'+label+'::ema'),torch.no_grad():torch._foreach_lerp_(ema,parameters,.01)
        for index,length,count in [(3,128,128),(7,256,64),(11,384,32),(15,512,16)]:
            meta=targets[index];record=read_record(meta['file'],meta['split'],meta['id'],embedding_dim=2560);batch=make_batch(record,meta,count,length)
            for self_condition in (False,True):
                if time.monotonic()-start>600:raise TimeoutError('kernel trace work cap')
                stem=f'L{length}::sc{int(self_condition)}';step(batch,self_condition,1729,'warmup::'+stem);torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats();ranges=[];durations=[]
                for rep in range(2):
                    label=stem+f'::rep{rep}';name='training_kernels::'+label;tick=time.monotonic()
                    with span(name):step(batch,self_condition,3000+rep,label);torch.cuda.synchronize()
                    durations.append(time.monotonic()-tick);ranges.append(dict(nvtx_range=name))
                row=dict(length=length,batch=count,self_condition=self_condition,batches=ranges,seconds=durations,peak_reserved_bytes=torch.cuda.max_memory_reserved(),peak_allocated_bytes=torch.cuda.max_memory_allocated())
                report['rows'].append(row);atomic_json(a.output/'profile.json',report);print(json.dumps({k:v for k,v in row.items() if k!='batches'}),flush=True)
            optimizer.zero_grad(set_to_none=True);del batch;gc.collect();torch.cuda.empty_cache()
        report['status']='complete'
    except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        report['seconds']=time.monotonic()-start;atomic_json(a.output/'profile.json',report)


if __name__=='__main__':main()
