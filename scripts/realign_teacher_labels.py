"""Reuse frozen teacher conformations, aligning poses before ProteinAE encoding."""
import argparse, hashlib, json, math, time
from pathlib import Path
import h5py, numpy as np, torch
from latentfold.backbone import align_backbone_to_reference, encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from profile_gpu import Telemetry, atomic_json
from predict import file_identity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'): p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());source=Path(c['source_manifest'])
    if hashlib.sha256(source.read_bytes()).hexdigest()!=c['source_manifest_sha256']:raise ValueError('source manifest changed')
    old=json.loads(source.read_text());labels=source.parent/'labels.h5'
    if old['status']!='complete' or old['config']['latent_frame']!='first_residue_N_CA_C' or len(old['records'])!=128:raise ValueError('invalid source shard')
    if file_identity(labels,hash_contents=True)['sha256']!=c['source_labels_sha256']:raise ValueError('source labels changed')
    protocol=Path(c['protocol'])
    if hashlib.sha256(protocol.read_bytes()).hexdigest()!=c['protocol_sha256']:raise ValueError('changed alignment protocol')
    if c['latent_frame'] not in ('teacher_CA_aligned_to_raw_reference','teacher_CA_aligned_to_cached_reference'):raise ValueError('invalid target frame')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0)
    torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,records=[],batches=[],controls=[],scope='Same frozen teacher conformations, explicit reference-aligned rigid poses (frame in config); no new sampling or rejection. Training labels only.')
    atomic_json(a.output/'manifest.json',m)
    try:
        selection=json.loads(Path(c['selection']).read_text())
        if hashlib.sha256(Path(c['selection']).read_bytes()).hexdigest()!=c['selection_sha256']:raise ValueError('changed family selection')
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True);tested=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(labels) as src,h5py.File(selection['dataset']) as inherited,h5py.File(a.output/'labels.h5','x') as out:
            for index,row in enumerate(sorted(old['records'],key=lambda r:-r['length'])):
                ident=row['id'];g=src[ident];n=row['length'];bucket=next(k for k in (128,256,384,512) if n<=k)
                reference=torch.from_numpy(g['reference_backbone'][:]).cuda();teacher=torch.from_numpy(g['teacher_backbone'][:]).cuda()
                cached_frame=c['latent_frame']=='teacher_CA_aligned_to_cached_reference'
                reference_target=g['raw_reference_z'][:]
                if cached_frame:
                    proxy=reference.clone();proxy[:,1]=torch.from_numpy(inherited['train'][ident]['ca_coords'][:]).cuda()
                    reference=align_backbone_to_reference(reference[None],proxy,torch.ones(n,dtype=torch.bool,device='cuda'))[0]
                    reference_target=inherited['train'][ident]['z'][:]
                    if (reference[:,1]-proxy[:,1]).square().sum(-1).mean().sqrt()>.02:raise ValueError('reference map disagrees with cached coordinates')
                valid=g['coarse_valid'][:].astype(bool);confidence=g['teacher_plddt'][:]
                if not valid.any():raise ValueError('expected source corpus with valid teacher samples')
                if confidence.shape!=(16,n) or not np.isfinite(confidence).all() or confidence.min()<0 or confidence.max()>1:raise ValueError('invalid teacher confidence')
                core=torch.from_numpy(confidence[valid].mean(0)>=.7).cuda();fallback=None
                if int(core.sum())<max(32,math.ceil(.5*n)):core=torch.ones(n,dtype=torch.bool,device='cuda');fallback='insufficient_confident_core'
                name=f'collect::reference_aligned::{index}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                try:
                    try:aligned=align_backbone_to_reference(teacher,reference,core)
                    except ValueError as error:
                        if 'degenerate' not in str(error):raise
                        core=torch.ones(n,dtype=torch.bool,device='cuda');fallback='degenerate_confident_core';aligned=align_backbone_to_reference(teacher,reference,core)
                    distances=torch.cdist(teacher[:,:,1],teacher[:,:,1],compute_mode='donot_use_mm_for_euclid_dist')
                    drift=(distances-torch.cdist(aligned[:,:,1],aligned[:,:,1],compute_mode='donot_use_mm_for_euclid_dist')).abs().max().item()
                    if drift>.005:raise ValueError('alignment changed internal distances')
                    mask=torch.ones(17,n,dtype=torch.bool,device='cuda');z=encode_backbone(decoder,torch.cat((reference[None],aligned)),mask)
                    reference_delta=(z[0]-torch.from_numpy(reference_target).cuda()).square().mean().sqrt().item()
                    if reference_delta>(.05 if cached_frame else 1e-4):raise ValueError('reference encoding parity failed')
                    z[0]=torch.from_numpy(reference_target).cuda()
                    noise=target_noise([ident],[4*n],3,seed=c['seed'],stream='reconstruction',device='cuda')*decoder.fm.scale_ref
                    rebuilt=decoder(z[:2],mask[:2],noise=noise.repeat(2,1,1)).cpu().numpy()
                    if bucket not in tested:
                        rotation=torch.tensor([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]],device='cuda');moved=teacher@rotation+torch.tensor([13.,-7.,19.],device='cuda')
                        recovered=align_backbone_to_reference(moved,reference,core);rz=encode_backbone(decoder,recovered,mask[1:]);coord=(recovered-aligned).abs().max().item();latent=(rz-z[1:]).square().mean().sqrt().item()
                        if coord>.005 or latent>1e-3:raise ValueError('rotation/encoding control failed')
                        m['controls'].append(dict(bucket=bucket,max_coordinate_error=coord,latent_rmse=latent));tested.add(bucket)
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                h=out.create_group(ident)
                for k,v in g.attrs.items():h.attrs[k]=v
                for k in ('raw_reference_z','teacher_plddt','coarse_valid','cluster'):h.create_dataset(k,data=g[k][:])
                h.create_dataset('reference_backbone',data=reference.cpu().numpy());h.create_dataset('reference_z',data=reference_target);h.create_dataset('teacher_backbone',data=aligned.cpu().numpy());h.create_dataset('teacher_z',data=z[1:].cpu().numpy())
                r=dict(row);r.update(native_reconstruction=ca_metrics(rebuilt[0],reference[:,1].cpu().numpy()),teacher_reconstruction=ca_metrics(rebuilt[1],teacher[0,:,1].cpu().numpy()),native_cached_latent_rmse=reference_delta if cached_frame else float(np.sqrt(np.mean((g['raw_reference_z'][:]-inherited['train'][ident]['z'][:])**2))),reference_encoding_parity_rmse=reference_delta,alignment_core_residues=int(core.sum()),alignment_fallback=fallback,max_distance_drift=drift)
                m['records'].append(r);m['batches'].append(dict(nvtx_range=name,seconds=seconds,length=n,batch=16,peak_reserved_bytes=torch.cuda.max_memory_reserved()));out.flush();atomic_json(a.output/'manifest.json',m);print(index+1,'of128',flush=True)
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('alignment work cap')
        if len(tested)!=4:raise ValueError('incomplete length-bucket rotation controls')
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
