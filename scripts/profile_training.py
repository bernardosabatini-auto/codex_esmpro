"""Bounded backward sizing and precision checks on fixed training records.

Profiles a deliberately expensive late-time, conditioned/self-conditioned draw.
No trained checkpoint is saved. Profile copies are not independent proteins.
"""
import argparse,json,time,os,gc
from pathlib import Path
import torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record,collate
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig
from latentfold.training import objective
from latentfold.precision import inference_precision
from profile_gpu import Telemetry,atomic_json


def make_batch(record,meta,count,padded_length=None):
    rows=[dict(record,id=f'{record["id"]}::copy{i}') for i in range(count)]
    batch=collate(rows)
    batch['adjacent']=torch.tensor([meta['adjacent']]*count,dtype=torch.bool)
    if padded_length is not None:
        extra=padded_length-batch['mask'].shape[1]
        if extra<0:raise ValueError('bucket shorter than target')
        for key in ('z','esm','ca'):batch[key]=F.pad(batch[key],(0,0,0,extra))
        for key in ('mask','adjacent'):batch[key]=F.pad(batch[key],(0,extra))
    return {k:v.cuda() if isinstance(v,torch.Tensor) else v for k,v in batch.items()}


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--source',type=Path,required=True)
    p.add_argument('--targets',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--diagnostic',type=Path,required=True);p.add_argument('--minutes',type=float,default=24)
    p.add_argument('--padded-buckets',action='store_true')
    p.add_argument('--candidate-precision',choices=['bf16','fp16'],default='bf16')
    p.add_argument('--profile-precision',choices=['fp32','fp16'],default='fp32')
    p.add_argument('--batches',nargs='+',type=int,default=[1,2,4,8,16,32])
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(0);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();deadline=start+60*a.minutes
    diagnostic=json.loads(a.diagnostic.read_text())
    if diagnostic['status']!='complete':raise ValueError('requires completed diagnostic')
    weight=diagnostic['candidate_weight_for_10pct_velocity_gradient']
    targets=json.loads(a.targets.read_text())['targets']
    report=dict(status='running',job_id=os.environ.get('SLURM_JOB_ID'),weight=weight,
        rows=[],precision_controls=[],batches=[],gpu=torch.cuda.get_device_name(0),
        gpu_bytes=torch.cuda.get_device_properties(0).total_memory,
        candidate_precision=a.candidate_precision,profile_precision=a.profile_precision,padded_buckets=a.padded_buckets,
        distribution='capacity stress: all conditioned, late t~0.88, self conditioning always; repeats 1')
    telemetry=None; active_range=False
    try:
        model,_=load_legacy(a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt',trusted_pickle=True)
        model.cuda().train();model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
        config=FlowConfig(condition_dropout=0,self_condition_probability=1,time_mean=2,time_std=.1)
        optimizer=torch.optim.AdamW(model.parameters(),lr=1e-5,weight_decay=.01,foreach=False)
        # Allocate real Adam state without changing weights, to account for memory.
        for parameter in model.parameters():
            optimizer.state[parameter].update(step=torch.tensor(0.),exp_avg=torch.zeros_like(parameter),exp_avg_sq=torch.zeros_like(parameter))
        telemetry=Telemetry(a.output,True);report['telemetry']=telemetry.info
        torch.cuda.nvtx.range_push('collect::backward_profile');active_range=True
        for index in (3,7,11,15):
            meta=targets[index];record=read_record(meta['file'],meta['split'],meta['id'],embedding_dim=2560)
            # Compare all parameter gradients with exactly shared draws at B=1.
            padded_length=128*(1+index//4) if a.padded_buckets else None
            reference=None;control={}
            for mode in ('fp32',a.candidate_precision):
                model.zero_grad(set_to_none=True);batch=make_batch(record,meta,1,padded_length)
                generator=torch.Generator(device='cuda').manual_seed(1729)
                with inference_precision(mode):
                    loss,stats=objective(model,decoder,batch,config,generator=generator,
                        geometry_weight=weight,geometry_seed=19)
                scale=128. if mode=='fp16' else 1.
                (loss*scale).backward()
                for parameter in model.parameters():
                    if parameter.grad is not None:parameter.grad.div_(scale)
                gradients={name:p.grad.detach().clone() for name,p in model.named_parameters() if p.grad is not None}
                if not all(torch.isfinite(g).all() for g in gradients.values()):raise FloatingPointError('nonfinite parameter gradient')
                if mode=='fp32':
                    reference=gradients;control.update(length=meta['length'],padded_length=padded_length,fp32_loss=float(loss.detach()))
                else:
                    if set(reference)!=set(gradients):raise ValueError('precision changed gradient coverage')
                    dot=sum((reference[k]*v).double().sum() for k,v in gradients.items())
                    rr=sum(v.double().square().sum() for v in reference.values())
                    gg=sum(v.double().square().sum() for v in gradients.values())
                    diff=sum((reference[k]-v).double().square().sum() for k,v in gradients.items())
                    control.update(candidate_loss=float(loss.detach()),candidate_precision=mode,gradient_cosine=float(dot/(rr*gg).sqrt()),relative_l2=float((diff/rr).sqrt()))
                    control['passed']=control['gradient_cosine']>=.99 and control['relative_l2']<=.1 and abs(control['candidate_loss']/control['fp32_loss']-1)<=.02
            model.zero_grad(set_to_none=True)
            with inference_precision('fp32'):
                flow_only,_=objective(model,decoder,batch,config,generator=torch.Generator(device='cuda').manual_seed(1729))
            flow_only.backward()
            norm_flow=sum(p.grad.double().square().sum() for p in model.parameters() if p.grad is not None)
            norm_aux=sum((reference[name]-p.grad).double().square().sum() for name,p in model.named_parameters() if p.grad is not None)
            control['weighted_aux_to_flow_parameter_grad_ratio']=float((norm_aux/norm_flow).sqrt())
            del flow_only
            report['precision_controls'].append(control)
            if a.profile_precision=='fp16' and not control['passed']:
                raise ValueError('FP16 parameter gradient control failed; no mixed-precision profiling promotion')
            del reference,gradients,batch,loss
            model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache()
            # Candidate precision is sized only after its backward control passes.
            # Promotion requires passing controls at every requested bucket.
            mode=a.profile_precision
            for arm in ('flow','geometry'):
                for count in a.batches:
                    if time.monotonic()>deadline:raise TimeoutError('internal profile time cap')
                    row=dict(length=padded_length or meta['length'],actual_length=meta['length'],target_id=meta['id'],batch=count,arm=arm,precision=mode)
                    try:
                        batch=make_batch(record,meta,count,padded_length);torch.cuda.reset_peak_memory_stats()
                        seconds=[]
                        for repetition in range(3):
                            model.zero_grad(set_to_none=True)
                            generator=torch.Generator(device='cuda').manual_seed(1729+repetition)
                            name=f'collect::train::{index}::{arm}::{count}::{repetition}'
                            torch.cuda.synchronize();tick=time.monotonic()
                            with inference_precision(mode):
                                loss,stats=objective(model,decoder,batch,config,generator=generator,
                                    geometry_weight=weight if arm=='geometry' else 0,geometry_seed=19,max_geometry=4)
                            scale=128. if mode=='fp16' else 1.
                            (loss*scale).backward()
                            for parameter in model.parameters():
                                if parameter.grad is not None:parameter.grad.div_(scale)
                            norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True)
                            # Optimizer allocations and arithmetic included; lr=0
                            # keeps the same reference weights throughout sizing.
                            optimizer.param_groups[0]['lr']=0.;optimizer.step()
                            torch.cuda.synchronize();seconds.append(time.monotonic()-tick)
                        peak=torch.cuda.max_memory_reserved();row.update(status='complete',seconds=sum(seconds)/3,
                            proteins_per_second=3*count/sum(seconds),peak_reserved_bytes=peak,
                            peak_allocated_bytes=torch.cuda.max_memory_allocated(),loss_stats=stats,gradient_norm=float(norm))
                        report['rows'].append(row)
                        print(json.dumps(row),flush=True)
                        del batch,loss
                        model.zero_grad(set_to_none=True);gc.collect();torch.cuda.empty_cache()
                        if peak>.80*report['gpu_bytes']:break
                    except torch.cuda.OutOfMemoryError:
                        # An OOM is a capacity boundary, never a successful case.
                        row['status']='out_of_memory';report['rows'].append(row)
                        model.zero_grad(set_to_none=True)
                        if 'loss' in locals(): del loss
                        if 'batch' in locals(): del batch
                        gc.collect();torch.cuda.empty_cache();break
                    atomic_json(a.output/'profile.json',report)
        report.update(status='complete',candidate_gradient_controls_passed=all(r['passed'] for r in report['precision_controls']))
    except BaseException as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if active_range:
            torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
            report['batches'].append(dict(nvtx_range='collect::backward_profile'))
        if telemetry:telemetry.close()
        report['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'profile.json',report)

if __name__=='__main__':main()
