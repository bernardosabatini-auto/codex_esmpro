"""Encode the same selected conformers in independent-PCA and fixed frames."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.backbone import encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from diagnose_pca_frames import frame
from audit_distill_labels import metrics
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());selection=json.loads(Path(c['selection']).read_text())
    if sha(c['selection'])!=c['selection_sha256'] or sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('source changed')
    if len(c['targets'])!=32 or not {r['id'] for r in c['targets']}<={r['id'] for r in selection['train']}:raise ValueError('training-only32 required')
    for path,expected in {(r['source_labels'],r['source_labels_sha256']) for r in c['targets']}:
        if sha(path)!=expected:raise ValueError('labels changed')
    a.output.mkdir(exist_ok=False,parents=True);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);tick=time.monotonic();telemetry=None
    m=dict(status='running',config=c,rows=[],batches=[],controls=[]);atomic_json(a.output/'manifest.json',m)
    try:
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True);tested=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'labels.h5','x') as out,h5py.File(c['embedding_cache']) as embeddings,h5py.File(selection['dataset']) as inherited:
            for index,r in enumerate(c['targets']):
                ident=r['id'];n=r['length']
                with h5py.File(r['source_labels']) as src:arrays={key:src[ident][key][:] for key in ('reference_z','reference_backbone','teacher_backbone','teacher_z','coarse_valid')}
                if not np.array_equal(arrays['reference_z'],inherited['train'][ident]['z'][:]):raise ValueError('cached reference identity changed')
                bb=arrays['teacher_backbone'];pca=np.stack([(x-x[:,1].mean(0)[None,None,:])@frame(x[:,1])[0] for x in bb]).astype('float32')
                name=f'collect::overfit_labels::{index}';torch.cuda.synchronize();start=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                try:
                    mask=torch.ones(16,n,dtype=torch.bool,device='cuda');pz=encode_backbone(decoder,torch.from_numpy(pca).cuda(),mask);az=torch.from_numpy(arrays['teacher_z']).cuda();noise=torch.cat([target_noise([ident],[4*n],3,seed=c['seed'],sample_index=k,stream='label_audit',device='cuda') for k in range(16)])*decoder.fm.scale_ref
                    audit={}
                    for label,z,reference in [('aligned',az,bb),('pca',pz,pca)]:
                        _,rebuilt=decoder(z,mask,noise=noise,return_backbone=True);vals=metrics(rebuilt,torch.from_numpy(reference).cuda());valid=arrays['coarse_valid'].astype(bool)
                        audit[label]=dict(mean_ca_lddt=vals['ca_lddt'].mean().item(),min_ca_lddt=vals['ca_lddt'].min().item(),decoded_valid=vals['coarse_valid'].sum().item(),input_valid=int(valid.sum()))
                        if r['bucket'] not in tested:
                            cpu=ca_metrics(rebuilt[0,:,1].cpu().numpy(),reference[0,:,1]);geometry=backbone_geometry(rebuilt.cpu().numpy());difference=abs(cpu['ca_lddt']-vals['ca_lddt'][0].item())
                            if difference>1e-5 or not np.array_equal(geometry['coarse_valid'],vals['coarse_valid'].cpu().numpy()):raise ValueError('GPU metric parity failed')
                            m['controls'].append(dict(bucket=r['bucket'],frame=label,lddt_difference=difference))
                    tested.add(r['bucket']);torch.cuda.synchronize();seconds=time.monotonic()-start
                finally:torch.cuda.nvtx.range_pop()
                g=out.create_group(ident);g.attrs['sequence_sha256']=r['sequence_sha256'];g.attrs['state_definition']=json.dumps(r['state_definition'])
                for key,value in dict(reference_z=arrays['reference_z'],reference_backbone=arrays['reference_backbone'],teacher_backbone=bb,teacher_z_aligned=arrays['teacher_z'],teacher_z_pca=pz.cpu().numpy(),coarse_valid=arrays['coarse_valid'],esm=embeddings['train'][ident]['80'][:]).items():g.create_dataset(key,data=value)
                m['rows'].append(dict(id=ident,**audit));m['batches'].append(dict(nvtx_range=name,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()));out.flush();atomic_json(a.output/'manifest.json',m);print('prepared',index+1,'of32',flush=True)
                if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('label preparation cap')
        m['audit']={arm:dict(ca_lddt=float(np.mean([r[arm]['mean_ca_lddt'] for r in m['rows']])),decoded_valid=sum(r[arm]['decoded_valid'] for r in m['rows'])/512,input_valid=sum(r[arm]['input_valid'] for r in m['rows'])/512) for arm in ('aligned','pca')}
        m['training_gate_passed']=all(x['ca_lddt']>=.98 and x['decoded_valid']>=x['input_valid']-.01 for x in m['audit'].values())
        if len(tested)!=4:raise ValueError('incomplete bucket controls')
        m['labels_sha256']=sha(a.output/'labels.h5');m['status']='complete'
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
