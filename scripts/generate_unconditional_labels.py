"""Generate unconditional teacher trajectories with no sequence or validity filtering."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.generative import sample_unconditional
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','parent_manifest','checkpoint','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    recipe=json.loads(Path(c['protocol']).read_text())
    if c['samples']!=recipe['labels_per_length'] or c['lengths']!=recipe['lengths'] or c['seed']!=recipe['label_seed'] or c['batch']!=16:raise ValueError('Wrong label recipe')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],batches=[],lengths=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'pairs.h5','x') as f:
            for n in c['lengths']:
                ident=f'unconditional_train_length{n}';g=f.create_group(str(n));g.attrs['noise_id']=ident
                for key,shape in [('noise',(c['samples'],n,8)),('endpoint',(c['samples'],n,8)),('backbone',(c['samples'],n,4,3))]:g.create_dataset(key,shape=shape,dtype='f4')
                for offset in range(0,c['samples'],c['batch']):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Unconditional label cap')
                    b=min(c['batch'],c['samples']-offset);mask=torch.ones(b,n,dtype=torch.bool,device='cuda');esm=torch.zeros(b,n,2560,device='cuda')
                    noise=torch.cat([target_noise([ident],[n],8,seed=c['seed'],sample_index=k,device='cuda') for k in range(offset,offset+b)]);dn=torch.cat([target_noise([ident],[4*n],3,seed=c['seed'],sample_index=k,stream='decoder',device='cuda') for k in range(offset,offset+b)])*decoder.fm.scale_ref
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();z=sample_unconditional(model,esm,mask,noise=noise,steps=50);_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb.cpu().numpy();torch.cuda.synchronize();m['batches'].append(dict(length=n,offset=offset,batch=b,seconds=time.monotonic()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    if offset==0:
                        generic=sample(model,esm[:1],mask[:1],SampleConfig(steps=50,guidance=0),noise=noise[:1]);alone=sample_unconditional(model,esm[:1],mask[:1],noise=noise[:1],steps=50);ca=decoder(generic,mask[:1],noise=dn[:1])[0].cpu().numpy();control=dict(length=n,latent_max_abs=float((generic-alone).abs().max()),**ca_metrics(bb[0,:,1],ca));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                        if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Teacher parity failed')
                    g['noise'][offset:offset+b]=noise.cpu().numpy();g['endpoint'][offset:offset+b]=z.cpu().numpy();g['backbone'][offset:offset+b]=bb;f.flush();atomic_json(a.output/'manifest.json',m)
                geometry=backbone_geometry(g['backbone'][:]);g.create_dataset('coarse_valid',data=geometry['coarse_valid']);m['lengths'].append(dict(length=n,samples=c['samples'],coarse_valid=float(geometry['coarse_valid'].mean())));atomic_json(a.output/'manifest.json',m);print('labeled',n,c['samples'],flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
