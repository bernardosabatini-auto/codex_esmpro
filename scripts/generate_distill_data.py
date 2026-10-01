"""Generate 16 teacher conformations and consistently encode verified references."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher import fast_features,load_fast_model
from latentfold.backbone import encode_backbone,canonical_backbone_frame
from latentfold.decoder import load_proteinae
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from benchmark_esmfold2 import backbone_indices
from summarize_ensemble import rmsd
from profile_gpu import Telemetry,atomic_json


def clusters(bb,valid):
    parent=list(range(len(bb)))
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for i in range(len(bb)):
        for j in range(i):
            if valid[i] and valid[j] and rmsd(bb[i,:,1],bb[j,:,1])<=2:parent[find(i)]=find(j)
    return [find(i) if valid[i] else -1 for i in range(len(bb))]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('selection','native_manifest','native_backbones','teacher_scores','student_scores','roundtrip_report'):
        if hashlib.sha256(Path(c[key]).read_bytes()).hexdigest()!=c[key+'_sha256']:raise ValueError('changed input '+key)
    if c.get('latent_frame')!='first_residue_N_CA_C':raise ValueError('canonical latent frame required')
    selection=json.loads(Path(c['selection']).read_text());native=json.loads(Path(c['native_manifest']).read_text());rt=json.loads(Path(c['roundtrip_report']).read_text())
    if native['status']!='complete' or len(native['records'])!=512 or native['selection_sha256']!=c['selection_sha256'] or rt['summaries']['3']['nearest_state_retained']<.95:raise ValueError('native verification/reconstruction gate closed')
    def coverage(key,setting):
        rows=[r for r in json.loads(Path(c[key]).read_text())['rows'] if r['setting']==setting and 'coverage' in r]
        if len(rows)!=16:raise ValueError('incomplete development coverage gate')
        return np.mean([r['coverage']['2.0']['32'] for r in rows])
    if coverage('teacher_scores','steps50')<=coverage('student_scores','cfg2/latent'):raise ValueError('teacher does not improve state coverage')
    shard=c['shard'];rows=selection['train'][shard::4]
    if shard not in range(4) or len(rows)!=128:raise ValueError('expected four disjoint 128-target shards')
    rows=sorted(rows,key=lambda r:-r['length']);a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,records=[],batches=[],scope='512-family teacher-label pilot; this shard has 128 targets,16 samples each. AFDB references and ESMFold2 predictions, not measured equilibrium populations. All samples retained, coarse-valid mask and native-free 2A RMSD clusters supplied.');atomic_json(a.output/'manifest.json',m)
    try:
        # Hashes were verified in the corrected teacher run before allocation here.
        for artifact in c['teacher_artifacts']:
            stat=Path(artifact['path']).stat()
            if stat.st_size!=artifact['bytes'] or stat.st_mtime_ns!=artifact['mtime_ns']:raise ValueError('teacher artifact changed since hash verification')
        model,loading=load_fast_model(a.source/'data/esmfold2_fast');m['teacher_adapter']=loading
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['native_backbones']) as natives,h5py.File(selection['dataset']) as inherited,h5py.File(a.output/'labels.h5','x') as output:
            for index,row in enumerate(rows):
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('label generation work cap')
                ident=row['id'];n=row['length'];seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{ident}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed)
                name=f'collect::distill_labels::{index}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                try:
                    features=fast_features(row['sequence']);atom_index=backbone_indices(features,n);prediction=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=16)
                    teacher=prediction.sample_atom_coords[:,torch.as_tensor(atom_index,device='cuda'),:].float();confidence=prediction.plddt.float().cpu().numpy();del prediction,features
                    if teacher.shape!=(16,n,4,3) or not torch.isfinite(teacher).all():raise ValueError('invalid teacher backbone')
                    reference=torch.from_numpy(natives[ident]['backbone'][:]).cuda();mask=torch.ones(17,n,device='cuda',dtype=torch.bool);coordinates=torch.cat((reference[None],teacher));encoded=encode_backbone(decoder,canonical_backbone_frame(coordinates),mask);raw_reference_z=encode_backbone(decoder,reference[None],mask[:1])[0].cpu().numpy()
                    noise=target_noise([ident],[4*n],3,seed=c['seed'],stream='reconstruction',device='cuda')*decoder.fm.scale_ref
                    rebuilt=decoder(encoded[:2],mask[:2],noise=noise.repeat(2,1,1)).cpu().numpy();teacher=teacher.cpu().numpy();reference=reference.cpu().numpy();encoded=encoded.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                geometry=backbone_geometry(teacher);labels=clusters(teacher,geometry['coarse_valid']);g=output.create_group(ident);g.attrs['sequence_sha256']=row['sequence_sha256'];g.attrs['seed']=seed
                for key,value in dict(reference_backbone=reference,teacher_backbone=teacher,reference_z=encoded[0],raw_reference_z=raw_reference_z,teacher_z=encoded[1:],teacher_plddt=confidence,coarse_valid=geometry['coarse_valid'],cluster=labels).items():g.create_dataset(key,data=value)
                native_error=ca_metrics(rebuilt[0],reference[:,1]);teacher_error=ca_metrics(rebuilt[1],teacher[0,:,1])
                m['records'].append(dict(id=ident,family=row['family'],length=n,valid_samples=int(geometry['coarse_valid'].sum()),teacher_clusters=len(set(labels)-{-1}),native_reconstruction=native_error,teacher_reconstruction=teacher_error,native_cached_latent_rmse=float(np.sqrt(np.mean((encoded[0]-inherited['train'][ident]['z'][:])**2)))))
                m['batches'].append(dict(nvtx_range=name,seconds=seconds,length=n,batch=16,peak_reserved_bytes=torch.cuda.max_memory_reserved()));output.flush();atomic_json(a.output/'manifest.json',m);print('teacher labels',index+1,'of',len(rows),flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
