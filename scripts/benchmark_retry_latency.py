"""Same-device resident sequence-to-backbone latency including geometry retries."""
import argparse,gc,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.embedding import FinalESMC
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from latentfold.teacher import fast_features,load_fast_model
from benchmark_esmfold2 import backbone_indices
from benchmark_ensemble_latency import BackboneReady
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json
from retry_latency_core import bounded_outputs


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','panel','quality_report','previous_timing_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if not json.loads(Path(c['quality_report']).read_text())['sampling_quality_gate_passed']:raise ValueError('External quality failed')
    if [h['name'] for h in c['retry_heads']]!=['original','compact500','reflow10']:raise ValueError('Wrong student roster')
    byid={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']};rows=[byid[i] for i in c['target_ids']]
    if len(rows)!=8 or len({r['family'] for r in rows})!=8:raise ValueError('Wrong timing panel')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,rows=[],batches=[],controls=[],device_name=torch.cuda.get_device_name(0),scope='Resident sequence-to-backbone, fresh ESM every prediction, FP32, all flow/decoder/transfer plus CPU geometry and up to4 retries included. Fixed32-slot noise addressing also used for K1/8 prefixes. Teacher trunk3/diffusion50 raw samples with validated confidence-free early exit. Loading, warmup, control comparisons and disk I/O excluded.');atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True)
        for head in c['retry_heads']+[dict(name='teacher')]:
            kind=head['name'];is_teacher=kind=='teacher'
            if not is_teacher:
                for key in ('checkpoint','ensemble_manifest','reference'):
                    if sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
                original=json.loads(Path(head['ensemble_manifest']).read_text())['config']
                if any(original[k]!=head[k] for k in ('checkpoint_sha256','flow_steps','primary_guidance','compact_condition','seed')):raise ValueError('Timing does not match qualified ensemble')
                embedding=FinalESMC(a.source/'data/esmc6b',precision='fp32');model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(original['decoder_checkpoint']),steps=3).cuda().eval()
            else:model,loading=load_fast_model(a.source/'data/esmfold2_fast');m['teacher_adapter']=loading;sampler=model._sample_structure
            with torch.no_grad(),inference_precision('fp32'):
                for row in rows:
                    ident=row['query_id'];n=row['length'];length=next(x for x in (128,256,384,512) if n<=x)
                    def predict(count):
                        seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:{count}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed)
                        if not is_teacher:
                            esm=embedding([row['sequence']],length);mask=torch.arange(length,device='cuda')[None]<n;dn=torch.zeros(1,4*length,3,device='cuda');dn[0,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                            def draw(addresses):
                                b=len(addresses);noise=torch.zeros(b,length,8,device='cuda')
                                for j,k in enumerate(addresses):noise[j,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=k,device='cuda')[0]
                                z=sample(model,esm.repeat(b,1,1),mask.repeat(b,1),SampleConfig(steps=head['flow_steps'],guidance=head['primary_guidance']),noise=noise,conditioning_ids=[ident]*b,compact_condition=head['compact_condition']);_,bb=decoder(z,mask.repeat(b,1),noise=dn.repeat(b,1,1),return_backbone=True)
                                return bb[:,:n].cpu().numpy()
                            return bounded_outputs(draw,count)
                        features=fast_features(row['sequence']);indices=backbone_indices(features,n);captured={};chunk=min(count,16)
                        def stop_after_backbone(**kwargs):captured.update(kwargs=kwargs,coordinates=sampler(**kwargs));raise BackboneReady()
                        model._sample_structure=stop_after_backbone
                        try:
                            try:model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=chunk)
                            except BackboneReady:pass
                        finally:model._sample_structure=sampler
                        if not captured:raise ValueError('Teacher sampler not reached')
                        coords=[captured['coordinates']]
                        for offset in range(chunk,count,chunk):coords.append(sampler(**dict(captured['kwargs'],num_diffusion_samples=min(chunk,count-offset))))
                        return torch.cat(coords)[:,torch.as_tensor(indices,device='cuda'),:].float().cpu().numpy(),dict(attempts=count,exhausted=0,selected_draws=list(range(count)))
                    warm={count:predict(count) for count in (1,8,32)}
                    if not is_teacher:
                        with h5py.File(head['reference']) as reference:g=reference[ident][f"cfg{head['primary_guidance']}/latent"];expected=g['backbone'][:];expected_indices=g['seed_indices'][:,0]
                        checks=[]
                        for count,(bb,info) in warm.items():
                            checks.extend(ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,expected[:count]))
                            if info['selected_draws']!=expected_indices[:count].tolist() or not np.array_equal(backbone_geometry(bb)['coarse_valid'],backbone_geometry(expected[:count])['coarse_valid']):raise ValueError('Retry prefix decisions changed')
                        control=dict(model=kind,target_id=ident,ca_rmsd=max(r['ca_rmsd'] for r in checks),ca_lddt=min(r['ca_lddt'] for r in checks),prefixes=[1,8,32],selected_indices_identical=True)
                        if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('Sequence/ensemble output parity failed')
                    else:
                        seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}:1".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed);features=fast_features(row['sequence']);indices=backbone_indices(features,n);full=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1).sample_atom_coords[:,torch.as_tensor(indices,device='cuda'),:].float().cpu().numpy();control=dict(model=kind,target_id=ident,**ca_metrics(warm[1][0][0,:,1],full[0,:,1]))
                        if control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Teacher full-fold parity failed')
                        del features,full
                    m['controls'].append(control)
                    for repeat in range(3):
                        counts=[1,8,32];counts=counts[repeat:]+counts[:repeat]
                        for count in counts:
                            if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Timing work cap')
                            torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();bb,info=predict(count);torch.cuda.synchronize();seconds=time.monotonic()-tick
                            if bb.shape!=(count,n,4,3) or not np.isfinite(bb).all() or info!=warm[count][1]:raise ValueError('Timed prediction decisions changed')
                            if any(ca_metrics(x[:,1],y[:,1])['ca_rmsd']>.01 for x,y in zip(bb,warm[count][0])):raise ValueError('Timed output changed')
                            record=dict(model=kind,target_id=ident,length=n,samples=count,repeat=repeat,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),**info);m['rows'].append(record);m['batches'].append(record)
                    atomic_json(a.output/'manifest.json',m);print(kind,ident,flush=True)
            if not is_teacher:del embedding,decoder
            else:del sampler
            del model;gc.collect();torch.cuda.empty_cache()
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
