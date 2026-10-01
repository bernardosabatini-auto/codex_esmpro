"""Compare AdamW kernel implementations while retaining validated checkpointing."""
import argparse,gc,json,time
from pathlib import Path
import torch
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record
from latentfold.decoder import load_proteinae
from profile_checkpointing import backward
from profile_training import make_batch
from profile_gpu import Telemetry,atomic_json


def optimizer_control(model):
    original=list(model.parameters())
    copies=[[p.detach().clone().requires_grad_() for p in original] for _ in range(2)]
    optimizers=[torch.optim.AdamW(params,lr=1e-5,weight_decay=.01,betas=(.9,.999),
        fused=fused,foreach=False) for params,fused in zip(copies,(False,True))]
    for params in copies:
        for source,p in zip(original,params):p.grad=source.grad.detach().clone() if source.grad is not None else None
    for _ in range(4):
        for optimizer in optimizers:optimizer.step()
    numerator=torch.zeros((),device='cuda',dtype=torch.float64);denominator=numerator.clone();maximum=numerator.clone()
    for old,a,b in zip(original,*copies):
        numerator+=(a-b).double().square().sum();denominator+=(old-a).double().square().sum()
        maximum=torch.maximum(maximum,(a-b).abs().max().double())
    relative=float((numerator/denominator).sqrt());absolute=float(maximum)
    return dict(relative_update_l2=relative,max_parameter_difference=absolute,passed=relative<=.02 and absolute<=2e-6,
        scope='Four optimizer updates with identical real clipped gradients and initial weights. This checks optimizer arithmetic, not a training trajectory.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--targets',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(0);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None
    report=dict(status='running',rows=[],controls=[],scope='FP16 head with fixed scale 128, original all-block activation recomputation, always self-conditioned stress. Compare single-tensor versus fused AdamW; no trained checkpoint saved.')
    try:
        model,_=load_legacy(a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt',trusted_pickle=True)
        model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
        targets=json.loads(a.targets.read_text())['targets'];telemetry=Telemetry(a.output,True)
        first=targets[3];record=read_record(first['file'],first['split'],first['id'],embedding_dim=2560)
        batch=make_batch(record,first,1,128);backward(model,decoder,batch,1729)
        control=optimizer_control(model);report['controls'].append(control);print(json.dumps(control),flush=True)
        model.zero_grad(set_to_none=True);del batch;gc.collect();torch.cuda.empty_cache()
        if not control['passed']:raise ValueError('fused optimizer arithmetic control failed')
        parameters=list(model.parameters());ema=[p.detach().clone() for p in parameters]
        for index,length,count in [(3,128,128),(7,256,64),(11,384,32),(15,512,16)]:
            meta=targets[index];record=read_record(meta['file'],meta['split'],meta['id'],embedding_dim=2560)
            for fused in (False,True):
                if time.monotonic()-start>900:raise TimeoutError('optimizer profile work cap')
                policy='fused_adamw' if fused else 'single_tensor_adamw'
                optimizer=torch.optim.AdamW(parameters,lr=0.,weight_decay=.01,betas=(.9,.999),foreach=False,fused=fused)
                batch=make_batch(record,meta,count,length)
                backward(model,decoder,batch,2718);optimizer.step();model.zero_grad(set_to_none=True)
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();durations=[];ranges=[]
                for rep in range(4):
                    name=f'optimizer_profile::{length}::{policy}::{count}::{rep}';torch.cuda.nvtx.range_push(name)
                    torch.cuda.synchronize();tick=time.monotonic()
                    try:
                        backward(model,decoder,batch,3000+rep);optimizer.step()
                        with torch.no_grad():torch._foreach_lerp_(ema,parameters,.01)
                        torch.cuda.synchronize();durations.append(time.monotonic()-tick)
                    finally:torch.cuda.nvtx.range_pop()
                    ranges.append(dict(nvtx_range=name))
                row=dict(length=length,batch=count,policy=policy,status='complete',seconds=sum(durations)/len(durations),
                    proteins_per_second=count*len(durations)/sum(durations),batches=ranges,
                    peak_reserved_bytes=torch.cuda.max_memory_reserved(),peak_allocated_bytes=torch.cuda.max_memory_allocated())
                report['rows'].append(row);atomic_json(a.output/'profile.json',report)
                print(json.dumps({k:v for k,v in row.items() if k!='batches'}),flush=True)
                model.zero_grad(set_to_none=True);del optimizer,batch;gc.collect();torch.cuda.empty_cache()
        report['status']='complete'
    except BaseException as error:report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        report['seconds']=time.monotonic()-start;atomic_json(a.output/'profile.json',report)


if __name__=='__main__':main()
