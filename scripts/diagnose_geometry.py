"""Bounded current-checkpoint decoder and auxiliary-gradient diagnostic.

Model weights remain frozen. Gradients are with respect to the predicted
velocity, not model parameters; a separate backward profile is required.
"""
import argparse, hashlib, json, os, time
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.data import read_record, collate
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise, sample, SampleConfig
from latentfold.geometry import legacy_lddt, revised_geometry, robust_distance
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from profile_gpu import Telemetry, atomic_json


def stats(g, flow):
    g,flow=g.flatten(),flow.flatten()
    return dict(norm=float(g.norm()), flow_cosine=float(F.cosine_similarity(g[None],flow[None])[0]),
                finite=bool(torch.isfinite(g).all()))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True); p.add_argument('--targets',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); p.add_argument('--minutes',type=float,default=24)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4); torch.manual_seed(0); torch.cuda.set_device(0)
    start=time.monotonic(); deadline=start+60*a.minutes
    manifest=json.loads(a.targets.read_text()); targets=manifest['targets']
    report=dict(status='running',job_id=os.environ.get('SLURM_JOB_ID'),targets=targets,
                manifest_sha256=hashlib.sha256(a.targets.read_bytes()).hexdigest(),
                times=[.15,.5,.75,.9], rows=[],sensitivity=[],batches=[],
                precision='strict FP32, actual frozen ProteinAE decoder backward',
                gradient_scope='velocity output; does not establish model-parameter backward precision',
                self_conditioning='one detached endpoint self-conditioning pass',
                expected_rows=len(targets)*8, torch=torch.__version__)
    telemetry=None
    try:
        records=[read_record(r['file'],r['split'],r['id'],embedding_dim=2560) for r in targets]
        for r,m in zip(records,targets):
            if r['sequence_sha256']!=m['sequence_sha256']: raise ValueError('input identity changed')
        data=a.source/'data/phase1_dataset'
        checkpoint=data/'last_pf_459M_p128x8_long512_scratch.ckpt'
        model, arch=load_legacy(checkpoint,trusted_pickle=True)
        model.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt').cuda()
        report.update(architecture=arch,checkpoint=str(checkpoint),gpu=torch.cuda.get_device_name(0),
                      gpu_bytes=torch.cuda.get_device_properties(0).total_memory)
        telemetry=Telemetry(a.output,True); report['telemetry']=telemetry.info
        with inference_precision('fp32'):
            for index,(record,meta) in enumerate(zip(records,targets)):
                if time.monotonic()>deadline: raise TimeoutError('internal diagnostic time cap')
                b=collate([record]); z,esm,mask,ref=[b[k].cuda() for k in ('z','esm','mask','ca')]
                adj=torch.tensor([meta['adjacent']],device='cuda',dtype=torch.bool)
                noise=target_noise(b['ids'],b['lengths'],8,seed=711,device='cuda')
                dn=target_noise(b['ids'],[4*n for n in b['lengths']],3,seed=711,stream='decoder',device='cuda')
                dn_other=target_noise(b['ids'],[4*n for n in b['lengths']],3,seed=712,stream='decoder',device='cuda')
                range_name=f'collect::diagnostic::{index}'
                torch.cuda.synchronize(); torch.cuda.nvtx.range_push(range_name)
                with torch.no_grad():
                    reconstruction=decoder(z,mask,noise=dn)
                    independent_ref=decoder(z,mask,noise=dn_other)
                    pair=model.compute_pair(esm,mask)
                reconstruct=ca_metrics(reconstruction[0].cpu().numpy(),ref[0].cpu().numpy())
                for t_value in report['times']:
                    for dropped in (False,True):
                        t=torch.tensor([t_value],device='cuda'); x=(1-t_value)*noise+t_value*z
                        drop=torch.tensor([dropped],device='cuda')
                        with torch.no_grad():
                            v0=model(x,t,esm,mask,drop,None,pair=pair)
                            sc=x+(1-t_value)*v0
                            velocity=model(x,t,esm,mask,drop,sc,pair=pair)
                        velocity=velocity.detach().requires_grad_()
                        flow=((velocity-(z-noise))**2).mean()
                        flow_g,=torch.autograd.grad(flow,velocity)
                        endpoint=F.layer_norm(x+(1-t_value)*velocity,(8,))
                        pred=decoder(endpoint,mask,noise=dn)
                        revised,nlocal=revised_geometry(pred,ref,mask,adj)
                        losses={'legacy_independent':legacy_lddt(pred,independent_ref,mask),
                                'legacy_paired':legacy_lddt(pred,reconstruction,mask),
                                'revised':revised}
                        gradients={k:torch.autograd.grad(v,velocity,retain_graph=i<2)[0]
                                   for i,(k,v) in enumerate(losses.items())}
                        row=dict(id=record['id'],length=len(record['sequence']),t=t_value,dropped=dropped,
                                 reconstruction=reconstruct,flow_loss=float(flow),flow_grad_norm=float(flow_g.norm()),
                                 local_quadruples=nlocal,losses={k:float(v.detach()) for k,v in losses.items()},
                                 gradients={k:stats(v,flow_g) for k,v in gradients.items()})
                        if any(not g['finite'] or g['norm']==0 for g in row['gradients'].values()):
                            raise FloatingPointError('zero or nonfinite auxiliary gradient')
                        if t_value>=.75 and not dropped:
                            with torch.no_grad():
                                row['endpoint_before']=ca_metrics(pred[0].cpu().numpy(),ref[0].cpu().numpy())
                                row['endpoint_descent']={}
                                for key,g in dict(flow=flow_g,**gradients).items():
                                    step=.05*g/(g.square().mean().sqrt()+1e-12)
                                    test_z=F.layer_norm(x+(1-t_value)*(velocity-step),(8,))
                                    test_ca=decoder(test_z,mask,noise=dn)
                                    row['endpoint_descent'][key]=ca_metrics(test_ca[0].cpu().numpy(),ref[0].cpu().numpy())
                        report['rows'].append(row)
                        del pred,endpoint,losses,gradients,revised,velocity
                # One representative from each length bucket: current full sample,
                # target interpolation, and equal-RMS target perturbations.
                if index%4==0:
                    with torch.no_grad():
                        sampled=sample(model,esm,mask,SampleConfig(25,2),noise=noise)
                        variants={'truth':z,'sample':sampled}
                        for fraction in (.25,.5,.75):
                            variants[f'interpolate_{fraction}']=F.layer_norm((1-fraction)*z+fraction*sampled,(8,))
                        for sigma in (.05,.2):
                            for direction in range(3):
                                perturb=target_noise(b['ids'],b['lengths'],8,seed=direction,stream='sensitivity',device='cuda')
                                perturb=perturb/perturb.square().mean().sqrt()
                                variants[f'perturb_{sigma}_{direction}']=F.layer_norm(z+sigma*perturb,(8,))
                        for key,value in variants.items():
                            ca=decoder(value,mask,noise=dn)
                            report['sensitivity'].append(dict(id=record['id'],variant=key,
                                latent_rms=float((value-z).square().mean().sqrt()),
                                **ca_metrics(ca[0].cpu().numpy(),ref[0].cpu().numpy())))
                torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
                report['batches'].append(dict(nvtx_range=range_name))
                report.update(elapsed_seconds=time.monotonic()-start,
                              peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                              peak_reserved_bytes=torch.cuda.max_memory_reserved())
                atomic_json(a.output/'diagnostic.json',report)
                print(json.dumps(dict(target=index+1,rows=len(report['rows']),seconds=report['elapsed_seconds'])),flush=True)
        if len(report['rows'])!=report['expected_rows']: raise ValueError('incomplete coverage')
        if any(p.grad is not None for p in decoder.parameters()): raise ValueError('decoder weights acquired gradients')
        report['status']='complete'
    except BaseException as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if telemetry: telemetry.close()
        report['elapsed_seconds']=time.monotonic()-start
        atomic_json(a.output/'diagnostic.json',report)

if __name__=='__main__': main()
