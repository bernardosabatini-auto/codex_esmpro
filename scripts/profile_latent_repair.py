"""Fixed training-only latent repair with no DiT or reference-structure loading."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from latent_repair import repair,accept
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    if sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('changed protocol')
    protocol=json.loads(Path(c['protocol']).read_text())
    if [s['job_id'] for s in c['sources']]!=protocol['training_jobs']:raise ValueError('source identity changed')
    for s in c['sources']:
        for k in ('manifest','predictions'):
            if sha(s[k])!=s[k+'_sha256']:raise ValueError('changed source')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,sources=[],batches=[],timing='All-family CPU screening plus conditional GPU repair, including conservative saved-output identity checks; excludes input/output disk, initial loading and valid-control checks.')
    atomic_json(a.output/'manifest.json',m)
    try:
        m['gpu']=torch.cuda.get_device_name(0)
        if 'RTX PRO 6000' not in m['gpu']:raise ValueError('RTX profile required')
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        with inference_precision('fp32'),h5py.File(a.output/'attempts.h5','x') as out:
            for source in c['sources']:
                rows={r['id']:r for r in source['targets']}
                if len(rows)!=122:raise ValueError('training coverage changed')
                controls={max((r for r in rows.values() if r['bucket']==b),key=lambda r:(r['length'],r['id']))['id'] for b in (128,256,384,512)}
                record=dict(job_id=source['job_id'],targets=[],controls=[],invalid=0,repaired=0);m['sources'].append(record)
                with h5py.File(source['predictions']) as h:
                    if set(h)!=set(rows):raise ValueError('saved prediction coverage changed')
                    for ident,r in rows.items():
                        if time.monotonic()-start>480:raise TimeoutError('latent repair work cap')
                        bb=h[ident]['cfg1']['backbone'][:];zs=h[ident]['cfg1']['z'][:];n=r['length'];length=r['bucket']
                        if bb.shape!=(32,n,4,3) or zs.shape!=(32,n,8):raise ValueError('saved shape changed')
                        def setup(k):
                            z=torch.zeros(1,length,8,device='cuda');z[0,:n]=torch.from_numpy(zs[k]).cuda();mask=torch.arange(length,device='cuda')[None]<n
                            noise=torch.zeros(1,4*length,3,device='cuda');noise[0,:4*n]=target_noise([ident],[4*n],3,seed=source['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                            with torch.no_grad():_,regen=decoder(z,mask,noise=noise,return_backbone=True)
                            regen=regen[0,:n].cpu().numpy();metrics=ca_metrics(regen[:,1],bb[k,:,1])
                            if metrics['ca_rmsd']>.2 or metrics['ca_lddt']<.99 or backbone_geometry(regen[None])['coarse_valid'][0]!=backbone_geometry(bb[k:k+1])['coarse_valid'][0]:raise ValueError('saved latent/noise decoder identity failed')
                            return z,mask,noise,metrics
                        if ident in controls:
                            valid=np.concatenate([backbone_geometry(bb[k:k+4])['coarse_valid'] for k in range(0,32,4)]);indices=np.flatnonzero(valid)
                            if not len(indices):raise ValueError('no valid control in declared family')
                            k=int(indices[0]);z,mask,noise,metrics=setup(k);unchanged,diag=repair(decoder,z,mask,noise,bb[k],protocol)
                            if not np.array_equal(unchanged,bb[k]) or diag['status']!='unchanged_valid':raise ValueError('valid control changed')
                            record['controls'].append(dict(id=ident,sample=k,**metrics));del z,mask,noise
                        torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();name=f"collect::latent_repair::{source['job_id']}::{ident}";torch.cuda.nvtx.range_push(name)
                        attempts=[]
                        try:
                            valid=np.concatenate([backbone_geometry(bb[k:k+4])['coarse_valid'] for k in range(0,32,4)])
                            for k in np.flatnonzero(~valid):
                                k=int(k);z,mask,noise,metrics=setup(k);candidate,diag=repair(decoder,z,mask,noise,bb[k],protocol)
                                if diag['status']=='repaired':
                                    if not accept(bb[k],candidate,protocol['acceptance'])[0]:raise ValueError('accepted output violates constraints')
                                elif not np.array_equal(candidate,bb[k]):raise ValueError('fallback changed')
                                attempts.append((k,candidate,dict(sample=k,control=metrics,**diag)));del z,mask,noise
                            torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        for k,candidate,diag in attempts:out.require_group(source['job_id']).require_group(ident).create_dataset(str(k),data=candidate)
                        repaired=sum(d['status']=='repaired' for _,_,d in attempts);record['invalid']+=len(attempts);record['repaired']+=repaired
                        record['targets'].append(dict(id=ident,seconds=seconds,invalid=len(attempts),repaired=repaired,attempts=[d for _,_,d in attempts]))
                        atomic_json(a.output/'manifest.json',m)
                if len(record['controls'])!=4 or len(record['targets'])!=122:raise ValueError('incomplete controls or scores')
                times=[r['seconds'] for r in record['targets']];record.update(mean_seconds_per32=float(np.mean(times)),max_seconds_per32=max(times),repaired_fraction=record['repaired']/record['invalid'] if record['invalid'] else 0.)
                gate=protocol['feasibility'];record['feasible']=record['repaired_fraction']>=gate['minimum_repaired_fraction_each_seed'] and record['mean_seconds_per32']<=gate['max_mean_seconds_per_32_samples'] and record['max_seconds_per32']<=gate['max_seconds_per_32_samples']
                print(json.dumps({k:v for k,v in record.items() if k not in ('targets','controls')}),flush=True)
        if any(p.grad is not None for p in decoder.parameters()):raise ValueError('decoder acquired gradients')
        m['qualified']=all(r['feasible'] for r in m['sources']) and max(r['peak_reserved_bytes'] for r in m['batches'])<=protocol['feasibility']['max_reserved_gib']*1024**3;m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
