"""Measure frozen autoencoder cycles without new teacher labels or optimization."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.backbone import encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from generate_isolated_motif import canonical_fragment
from generate_generative_pilot import motif_error
from prepare_roundtrip_designability import audit_sources
from profile_gpu import atomic_json,Telemetry


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_sources(c);a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],controls=[]);telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['inputs']) as f,h5py.File(a.output/'roundtrips.h5','x') as out:
            for r in c['entries']:
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Diagnostic cap')
                raw=f[r['name']][:];canonical,degenerate=canonical_fragment(raw.astype(np.float64));n=len(raw);mask=torch.ones(1,n,dtype=torch.bool,device='cuda');torch.cuda.synchronize();tick=time.monotonic();z=F.layer_norm(encode_backbone(decoder,torch.from_numpy(canonical)[None].cuda(),mask),(8,))
                if r['name'] in c['control_names']:
                    rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=np.float64);posed,_=canonical_fragment(raw.astype(np.float64)@rotation+np.array([11,7,-3]));zp=F.layer_norm(encode_backbone(decoder,torch.from_numpy(posed)[None].cuda(),mask),(8,));control=dict(name=r['name'],coordinate_max_abs=float(np.max(abs(canonical-posed))),latent_rmse=float((z-zp).square().mean().sqrt()));m['controls'].append(control)
                    if control['coordinate_max_abs']>1e-4 or control['latent_rmse']>1e-4:raise ValueError('Roundtrip rigid-pose control failed')
                for k in range(2):
                    noise=target_noise([f"{r['cohort']}:{r['target_id']}:{r['slot']}"],[4*n],3,seed=c['seed'],sample_index=k,stream='designability_cycle',device='cuda')*decoder.fm.scale_ref;_,bb=decoder(z,mask,noise=noise,return_backbone=True);bb=bb[0].cpu().numpy();out.create_dataset(r['name']+'/'+str(k),data=bb);metrics=ca_metrics(bb[:,1],raw[:,1]);drms=float(motif_error(bb[None],raw,np.ones(n,bool))[0]);m['records'].append(dict(name=r['name'],sample_index=k,near_degenerate=degenerate,distance_rms=drms,**metrics))
                torch.cuda.synchronize();m.setdefault('timings',[]).append(dict(name=r['name'],seconds=time.monotonic()-tick));out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
