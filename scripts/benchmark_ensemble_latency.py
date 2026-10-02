"""Matched resident-model sequence-to-backbone ensemble latency on one GPU."""
import argparse,gc,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.embedding import FinalESMC
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from latentfold.teacher import fast_features,load_fast_model
from benchmark_esmfold2 import backbone_indices
from profile_gpu import Telemetry,atomic_json
from predict import file_identity


class BackboneReady(Exception):
    pass


def main():
    p=argparse.ArgumentParser()
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['panel'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['panel_sha256']:raise ValueError('changed panel')
    for field in ('candidate_reference','quality_report','candidate_manifest','timing_protocol'):
        if c.get(field+'_sha256') and file_identity(Path(c[field]),hash_contents=True)['sha256']!=c[field+'_sha256']:raise ValueError('changed '+field)
    if c.get('quality_report') and not json.loads(Path(c['quality_report']).read_text())['sampling_quality_gate_passed']:raise ValueError('candidate ensemble quality gate failed')
    byid={r['query_id']:r for r in json.loads(path.read_text())['development']};rows=[byid[i] for i in c['target_ids']]
    if len(rows)!=8 or len({r['family'] for r in rows})!=8:raise ValueError('eight development families required')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,rows=[],batches=[],controls=[],scope='Resident-model sequence-to-backbone latency, batch one sequence, K1/8/32, strict FP32. Includes sequence features, ESMC, trunk/flow, decoder, and output transfer. Teacher confidence heads omitted using validated early exit after backbone sampling. Loading, warmup, control comparisons and disk writes excluded from timed ranges.');atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True)
        m['device_name']=torch.cuda.get_device_name(0)
        for kind in (('student','candidate','teacher') if c.get('candidate_checkpoint') else ('student','teacher')):
            if kind in ('student','candidate'):
                checkpoint=Path(c['candidate_checkpoint']) if kind=='candidate' else Path(c['student_checkpoint']) if c.get('student_checkpoint') else a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt'
                identity=file_identity(checkpoint,hash_contents=True);m[kind+'_checkpoint']=identity
                if c.get(kind+'_checkpoint_sha256') and identity['sha256']!=c[kind+'_checkpoint_sha256']:raise ValueError(kind+' checkpoint changed')
                embedding=FinalESMC(a.source/'data/esmc6b',precision='fp32');model,_=load_legacy(checkpoint,trusted_pickle=True);model.cuda().eval().requires_grad_(False)
                decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
            else:
                model,loading=load_fast_model(a.source/'data/esmfold2_fast');m['teacher_adapter']=loading;sampler=model._sample_structure
            with torch.no_grad(),inference_precision('fp32'):
                for row in rows:
                    ident=row['query_id'];n=row['length'];length=next(x for x in (128,256,384,512) if n<=x)
                    def predict(count):
                        seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:{count}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed)
                        if kind in ('student','candidate'):
                            esm=embedding([row['sequence']],length);mask=torch.arange(length,device='cuda')[None]<n
                            noise=torch.zeros(count,length,8,device='cuda');dn=torch.zeros(count,4*length,3,device='cuda')
                            for k in range(count):
                                noise[k,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=k,device='cuda')[0]
                                dn[k,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                            z=sample(model,esm.repeat(count,1,1),mask.repeat(count,1),SampleConfig(steps=c['candidate_steps'] if kind=='candidate' else 25,guidance=c.get('candidate_guidance',1) if kind=='candidate' else 2,solver=c.get('candidate_solver','euler') if kind=='candidate' else 'euler',time_power=c.get('candidate_time_power',1) if kind=='candidate' else 1),noise=noise,conditioning_ids=[ident]*count)
                            _,bb=decoder(z,mask.repeat(count,1),noise=dn,return_backbone=True)
                            return bb[:,:n].cpu().numpy()
                        features=fast_features(row['sequence']);indices=backbone_indices(features,n);captured={};chunk=min(count,16)
                        def stop_after_backbone(**kwargs):
                            captured['kwargs']=kwargs;captured['coordinates']=sampler(**kwargs);raise BackboneReady()
                        model._sample_structure=stop_after_backbone
                        try:
                            try:model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=chunk)
                            except BackboneReady:pass
                        finally:model._sample_structure=sampler
                        if not captured:raise ValueError('teacher sampler was not reached')
                        coordinates=[captured['coordinates']]
                        for offset in range(chunk,count,chunk):coordinates.append(sampler(**dict(captured['kwargs'],num_diffusion_samples=min(chunk,count-offset))))
                        return torch.cat(coordinates)[:,torch.as_tensor(indices,device='cuda'),:].float().cpu().numpy()
                    # Warm both capacity regimes; retain an exact teacher full-fold control.
                    warm=predict(1);predict(32)
                    if kind in ('student','candidate'):
                        with h5py.File(c['candidate_reference'] if kind=='candidate' else c['student_reference']) as reference:expected=reference[ident][f"cfg{c.get('candidate_guidance',1)}/latent/backbone" if kind=='candidate' else 'cfg2/latent/backbone'][0]
                        control=ca_metrics(warm[0,:,1],expected[:,1]);m['controls'].append(dict(model=kind,target_id=ident,**control))
                        if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('student sequence-to-ensemble parity failed')
                    if kind=='teacher':
                        seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:1".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed);features=fast_features(row['sequence']);indices=backbone_indices(features,n);full=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1).sample_atom_coords[:,torch.as_tensor(indices,device='cuda'),:].float().cpu().numpy();control=ca_metrics(warm[0,:,1],full[0,:,1]);m['controls'].append(dict(model=kind,target_id=ident,**control))
                        if control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('teacher structure-only parity failed')
                        del full,features
                    for repeat in range(3):
                        # Rotate count order between repeats to reduce monotonic clock drift.
                        counts=[1,8,32];counts=counts[repeat:]+counts[:repeat]
                        for count in counts:
                            if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('timing work cap')
                            name=f'collect::latency::{kind}::{ident}::{repeat}::{count}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                            try:bb=predict(count);torch.cuda.synchronize();seconds=time.monotonic()-tick
                            finally:torch.cuda.nvtx.range_pop()
                            if bb.shape!=(count,n,4,3) or not np.isfinite(bb).all():raise ValueError('invalid timed backbone')
                            r=dict(model=kind,target_id=ident,length=n,samples=count,repeat=repeat,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),nvtx_range=name);m['rows'].append(r);m['batches'].append(r)
                    atomic_json(a.output/'manifest.json',m);print(kind,ident,flush=True)
            if kind in ('student','candidate'):del embedding,decoder
            else:del sampler
            del model;gc.collect();torch.cuda.empty_cache()
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
