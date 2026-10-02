"""Fresh ESMC80 and16 teacher draws with cached-frame labels and full audit."""
import argparse,gc,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.embedding import FinalESMC
from latentfold.teacher import fast_features,load_fast_model
from latentfold.backbone import align_backbone_to_reference,encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from benchmark_esmfold2 import backbone_indices
from audit_distill_labels import metrics
from expansion_data import eligibility,reconstruction_summary
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def verify(c):
    for key,value in c.items():
        if key.endswith('_sha256') and key[:-7] in c:
            if sha(c[key[:-7]])!=value:raise ValueError('changed '+key[:-7])
    for r in c['controls']:
        for key in ('raw_manifest','raw_labels'):
            if sha(r[key])!=r[key+'_sha256']:raise ValueError('changed historical control')
    for artifact in c['teacher_artifacts']+c['embedding_artifacts']:
        s=Path(artifact['path']).stat()
        if s.st_size!=artifact['bytes'] or s.st_mtime_ns!=artifact['mtime_ns']:raise ValueError('changed model artifact')
    targets=c['targets'];controls=c['controls'];selection=json.loads(Path(c['selection']).read_text())
    allowed={r['id']:r for r in selection['train']}
    if len({r['id'] for r in targets+controls})!=len(targets)+len(controls):raise ValueError('duplicate target/control')
    for r in targets:
        if {k:v for k,v in r.items() if k!='control'}!=allowed.get(r['id']) or r['control']:raise ValueError('candidate not in audited selection')
    old=json.loads(Path(c['old_selection']).read_text());allowed_old={r['id']:r for r in old['train']}
    if len(controls)!=4 or {r['bucket'] for r in controls}!={128,256,384,512}:raise ValueError('missing historical bucket controls')
    for r in controls:
        if any(r.get(k)!=v for k,v in allowed_old.get(r['id'],{}).items()) or r['id'] not in allowed_old or not r['control']:raise ValueError('control not in old training')
    return selection,old


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());selection,oldselection=verify(c)
    recipe=json.loads(Path(c['protocol']).read_text());tol=recipe['controls']
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,records=[],batches=[],controls=[],embedding_controls=[],rotation_controls=[],metric_controls=[],scope='Training-only teacher labels; not measured physical populations or student generalization.')
    atomic_json(a.output/'manifest.json',m)
    def deadline():
        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('generation work cap')
    def measure(name,fn,**metadata):
        deadline();torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
        try:result=fn();torch.cuda.synchronize()
        finally:torch.cuda.nvtx.range_pop()
        m['batches'].append(dict(nvtx_range=name,seconds=time.monotonic()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved(),**metadata));return result
    try:
        telemetry=Telemetry(a.output,True);rows=c['controls']+c['targets']
        encoder=FinalESMC(a.source/'data/esmc6b',precision='fp32')
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'embeddings.h5','x') as out,h5py.File(c['old_embedding_cache']) as previous:
            group=out.create_group('train')
            for bucket in (128,256,384,512):
                cohort=[r for r in rows if r['bucket']==bucket]
                for offset in range(0,len(cohort),8):
                    chunk=cohort[offset:offset+8]
                    values=measure(f'collect::new_embedding::{bucket}::{offset}',lambda:encoder([r['sequence'] for r in chunk],bucket).cpu().numpy(),phase='embedding',length=bucket,batch=len(chunk))
                    for i,r in enumerate(chunk):
                        value=values[i,:r['length']];g=group.create_group(r['id']);g.attrs['sequence_sha256']=r['sequence_sha256'];g.create_dataset('80',data=value)
                        if r['control']:
                            delta=value-previous['train'][r['id']]['80'][:];rmse=float(np.sqrt(np.mean(delta**2)));maximum=float(np.abs(delta).max())
                            m['embedding_controls'].append(dict(id=r['id'],bucket=bucket,rmse=rmse,max_abs=maximum))
                            if rmse>tol['embedding_rmse'] or maximum>tol['embedding_max_abs']:raise ValueError('fresh embedding control failed')
                    del values
                out.flush();atomic_json(a.output/'manifest.json',m)
        del encoder;gc.collect();torch.cuda.empty_cache()
        model,adapter=load_fast_model(a.source/'data/esmfold2_fast');m['teacher_adapter']=adapter
        decoder=load_proteinae(a.source/'ProteinAE_v1',c['decoder_checkpoint'],steps=3).cuda()
        tested=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(selection['dataset']) as inherited,h5py.File(oldselection['dataset']) as inherited_old,h5py.File(c['native_backbones']) as sources,h5py.File(c['old_native_backbones']) as oldsources,h5py.File(a.output/'labels.h5','x') as output:
            # Longest structures first exercise maximum teacher memory before most work.
            for index,r in enumerate(sorted(rows,key=lambda r:(-r['length'],r['id']))):
                ident=r['id'];n=r['length'];bucket=r['bucket']
                seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}".encode()).digest()[:8],'little')%(2**63-1)
                def fold():
                    torch.manual_seed(seed);features=fast_features(r['sequence']);indices=backbone_indices(features,n)
                    prediction=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=16)
                    teacher=prediction.sample_atom_coords[:,torch.as_tensor(indices,device='cuda'),:].float();confidence=prediction.plddt.float().cpu().numpy()
                    if teacher.shape!=(16,n,4,3) or not torch.isfinite(teacher).all():raise ValueError('invalid teacher output')
                    return teacher,confidence
                teacher,confidence=measure(f'collect::new_teacher::{index}',fold,phase='teacher',length=n,bucket=bucket,batch=16,control=r['control'])
                raw=teacher.cpu().numpy();valid=backbone_geometry(raw)['coarse_valid']
                if r['control']:
                    with h5py.File(r['raw_labels']) as previous:
                        oldbb=previous[ident]['teacher_backbone'][:];oldvalid=previous[ident]['coarse_valid'][:]
                    scores=[ca_metrics(raw[k,:,1],oldbb[k,:,1]) for k in range(16)]
                    control=dict(id=ident,bucket=bucket,max_ca_rmsd=max(x['ca_rmsd'] for x in scores),min_ca_lddt=min(x['ca_lddt'] for x in scores),validity_exact=bool(np.array_equal(valid,oldvalid)))
                    m['controls'].append(control)
                    if control['max_ca_rmsd']>tol['teacher_ca_rmsd'] or control['min_ca_lddt']<tol['teacher_ca_lddt'] or not control['validity_exact']:raise ValueError('historical teacher draw control failed')
                src=oldsources if r['control'] else sources;cache=inherited_old if r['control'] else inherited
                reference=torch.from_numpy(src[ident]['backbone'][:]).cuda();cached=cache['train'][ident];reference_z=cached['z'][:]
                for key in ('z','ca_coords'):
                    if hashlib.sha256(cached[key][:].tobytes()).hexdigest()!=r['array_sha256'][key]:raise ValueError('cached source array changed')
                proxy=reference.clone();proxy[:,1]=torch.from_numpy(cached['ca_coords'][:]).cuda();all_residues=torch.ones(n,device='cuda',dtype=torch.bool)
                reference=align_backbone_to_reference(reference[None],proxy,all_residues)[0]
                ca_error=(reference[:,1]-proxy[:,1]).square().sum(-1).mean().sqrt().item()
                if ca_error>tol['reference_ca_rmsd']:raise ValueError('cached reference frame mismatch')
                core=torch.from_numpy(confidence[valid].mean(0)>=.7).cuda() if valid.any() else all_residues;fallback=None
                if not valid.any() or int(core.sum())<max(32,math.ceil(n/2)):core=all_residues;fallback='insufficient_confident_core'
                def encode_and_audit():
                    nonlocal core,fallback
                    try:aligned=align_backbone_to_reference(teacher,reference,core)
                    except ValueError as error:
                        if 'degenerate' not in str(error):raise
                        core=all_residues;fallback='degenerate_confident_core';aligned=align_backbone_to_reference(teacher,reference,core)
                    drift=(torch.cdist(teacher[:,:,1],teacher[:,:,1],compute_mode='donot_use_mm_for_euclid_dist')-torch.cdist(aligned[:,:,1],aligned[:,:,1],compute_mode='donot_use_mm_for_euclid_dist')).abs().max().item()
                    if drift>tol['internal_distance_drift']:raise ValueError('alignment altered distances')
                    mask=torch.ones(17,n,device='cuda',dtype=torch.bool);z=encode_backbone(decoder,torch.cat((reference[None],aligned)),mask)
                    parity=(z[0]-torch.from_numpy(reference_z).cuda()).square().mean().sqrt().item()
                    if parity>tol['reference_z_rmse']:raise ValueError('reference latent parity failed')
                    z[0]=torch.from_numpy(reference_z).cuda()
                    noise=target_noise([ident],[4*n],3,seed=c['seed'],stream='reconstruction',device='cuda').repeat(16,1,1)*decoder.fm.scale_ref
                    _,rebuilt=decoder(z[1:],mask[1:],noise=noise,return_backbone=True);audit={k:v.cpu().numpy() for k,v in metrics(rebuilt,aligned).items()}
                    if not all(np.isfinite(v).all() for v in audit.values()):raise ValueError('nonfinite reconstruction')
                    if bucket not in tested:
                        rotation=torch.tensor([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]],device='cuda');moved=teacher@rotation+torch.tensor([13.,-7.,19.],device='cuda')
                        recovered=align_backbone_to_reference(moved,reference,core);rz=encode_backbone(decoder,recovered,mask[1:])
                        coord=(recovered-aligned).abs().max().item();latent=(rz-z[1:]).square().mean().sqrt().item()
                        m['rotation_controls'].append(dict(bucket=bucket,max_coordinate_error=coord,latent_rmse=latent))
                        if coord>tol['rotation_coordinate_max'] or latent>tol['rotation_latent_rmse']:raise ValueError('rotation control failed')
                        expected=ca_metrics(rebuilt[0,:,1].cpu().numpy(),aligned[0,:,1].cpu().numpy());delta=max(abs(audit[k][0]-expected[k]) for k in ('ca_lddt','ca_rmsd'))
                        same=bool(np.array_equal(backbone_geometry(rebuilt.cpu().numpy())['coarse_valid'],audit['coarse_valid']))
                        m['metric_controls'].append(dict(bucket=bucket,max_metric_difference=float(delta),validity_exact=same))
                        if delta>tol['gpu_cpu_metric_difference'] or not same:raise ValueError('CPU metric control failed')
                        tested.add(bucket)
                    return aligned.cpu().numpy(),z.cpu().numpy(),audit,drift,parity
                aligned,z,audit,drift,parity=measure(f'collect::new_encode_audit::{index}',encode_and_audit,phase='encode_audit',length=n,bucket=bucket,batch=16,control=r['control'])
                state,reason=eligibility(aligned,valid,confidence)
                g=output.create_group(ident);g.attrs['sequence_sha256']=r['sequence_sha256'];g.attrs['seed']=seed;g.attrs['control']=r['control']
                for key,value in dict(reference_backbone=reference.cpu().numpy(),reference_z=reference_z,teacher_backbone=aligned,teacher_z=z[1:],teacher_plddt=confidence,coarse_valid=valid).items():g.create_dataset(key,data=value)
                record=dict(id=ident,family=r['family'],length=n,bucket=bucket,control=r['control'],eligible=state is not None,exclusion_reason=reason,state_definition=state,mean_teacher_confidence=float(confidence.mean()),valid_samples=int(valid.sum()),reference_ca_error=ca_error,reference_encoding_parity_rmse=parity,alignment_core_residues=int(core.sum()),alignment_fallback=fallback,max_distance_drift=drift,reconstruction={k:v.tolist() for k,v in audit.items()})
                m['records'].append(record);output.flush();atomic_json(a.output/'manifest.json',m);print('audited',index+1,'of',len(rows),ident,'eligible',state is not None,flush=True)
                del teacher,reference,proxy,aligned,z,audit,raw
        if any(len(m[key])!=4 for key in ('controls','embedding_controls','rotation_controls','metric_controls')):raise ValueError('incomplete bucket controls')
        m['reconstruction']=reconstruction_summary([r for r in m['records'] if not r['control']])
        m['resource_gate_passed']=max(b['peak_reserved_bytes'] for b in m['batches'])<=110*1024**3
        m['labels_sha256']=sha(a.output/'labels.h5');m['embeddings_sha256']=sha(a.output/'embeddings.h5');m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
