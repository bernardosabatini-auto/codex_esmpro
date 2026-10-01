"""Measure the memory/speed tradeoff from recomputing only the pair track."""
import argparse,gc,json,time
from pathlib import Path
import torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.data import read_record
from latentfold.flow import FlowConfig
from latentfold.training import objective,controlled_backward
from latentfold.precision import inference_precision
from profile_training import make_batch
from profile_gpu import Telemetry,atomic_json


def backward(model,decoder,batch,seed):
    model.zero_grad(set_to_none=True)
    generator=torch.Generator(device='cuda').manual_seed(seed)
    with inference_precision('fp16'):
        loss,_,_=objective(model,decoder,batch,FlowConfig(self_condition_probability=1),generator=generator,return_parts=True)
    controlled_backward(model,loss,None,weight=0,loss_scale=128.)
    torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
    return float(loss.detach())


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--targets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(0);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    started=time.monotonic();report=dict(status='running',controls=[],rows=[],gpu_bytes=torch.cuda.get_device_properties(0).total_memory,
        scope='FP16 head, fixed scale 128, always self-conditioned capacity stress. Real Adam and EMA storage/arithmetic. Repeated profile inputs are not independent proteins.')
    telemetry=None
    try:
        model,_=load_legacy(a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt',trusted_pickle=True)
        model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
        optimizer=torch.optim.AdamW(model.parameters(),lr=0.,weight_decay=.01,foreach=False)
        for parameter in model.parameters():optimizer.state[parameter].update(step=torch.tensor(0.),exp_avg=torch.zeros_like(parameter),exp_avg_sq=torch.zeros_like(parameter))
        ema=[p.detach().clone() for p in model.parameters()];parameters=list(model.parameters())
        targets=json.loads(a.targets.read_text())['targets'];telemetry=Telemetry(a.output,True)
        for index,bucket,count in [(3,128,128),(7,256,64),(11,384,32),(15,512,16)]:
            meta=targets[index];record=read_record(meta['file'],meta['split'],meta['id'],embedding_dim=2560)
            batch=make_batch(record,meta,1,bucket)
            model.checkpoint_blocks=True;base_loss=backward(model,decoder,batch,1729)
            reference={n:p.grad.detach().clone() for n,p in model.named_parameters() if p.grad is not None}
            model.checkpoint_blocks=False;candidate_loss=backward(model,decoder,batch,1729)
            diff=torch.zeros((),device='cuda',dtype=torch.float64);norm=torch.zeros_like(diff)
            for n,p in model.named_parameters():
                if n in reference:
                    if p.grad is None:raise ValueError('gradient coverage changed')
                    diff+=(reference[n]-p.grad).double().square().sum();norm+=reference[n].double().square().sum()
            relative=float((diff/norm).sqrt());control=dict(length=bucket,relative_gradient_l2=relative,loss_change=candidate_loss-base_loss,
                passed=relative<1e-4 and abs(candidate_loss-base_loss)<1e-5)
            report['controls'].append(control);print('gradient_control',json.dumps(control),flush=True)
            del reference,batch;model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache()
            if not control['passed']:raise ValueError('recomputation gradient equivalence failed')
            for policy,n in [('all_blocks',count),('pair_only',count//2),('pair_only',count)]:
                if time.monotonic()-started>900:raise TimeoutError('profile time budget')
                model.checkpoint_blocks=policy=='all_blocks';row=dict(length=bucket,batch=n,policy=policy,batches=[])
                try:
                    batch=make_batch(record,meta,n,bucket)
                    backward(model,decoder,batch,2718);optimizer.step();model.zero_grad(set_to_none=True)
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();durations=[]
                    for rep in range(4):
                        name=f'checkpoint_profile::{bucket}::{policy}::{n}::{rep}'
                        torch.cuda.nvtx.range_push(name);torch.cuda.synchronize();tick=time.monotonic()
                        try:
                            backward(model,decoder,batch,3000+rep);optimizer.step()
                            with torch.no_grad():torch._foreach_lerp_(ema,parameters,.01)
                            torch.cuda.synchronize();durations.append(time.monotonic()-tick)
                        finally:torch.cuda.nvtx.range_pop()
                        row['batches'].append(dict(nvtx_range=name))
                    row.update(status='complete',seconds=sum(durations)/len(durations),proteins_per_second=n*len(durations)/sum(durations),peak_reserved_bytes=torch.cuda.max_memory_reserved(),peak_allocated_bytes=torch.cuda.max_memory_allocated())
                except torch.cuda.OutOfMemoryError:
                    row.update(status='out_of_memory')
                finally:
                    model.zero_grad(set_to_none=True)
                    if 'batch' in locals():del batch
                    gc.collect();torch.cuda.empty_cache()
                report['rows'].append(row);atomic_json(a.output/'profile.json',report);print(json.dumps({k:v for k,v in row.items() if k!='batches'}),flush=True)
        report['status']='complete'
    except BaseException as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        report['seconds']=time.monotonic()-started;atomic_json(a.output/'profile.json',report)


if __name__=='__main__':main()
