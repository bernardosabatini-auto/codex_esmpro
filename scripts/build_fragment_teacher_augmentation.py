"""Decode every eligible teacher endpoint before it can supervise training."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from prepare_fragment_teacher_augmentation import audit_config
from fragment_teacher_augmentation_core import qualifying_states
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_config(c);a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[],controls=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['candidates']) as src,h5py.File(c['fragments']) as fr,h5py.File(a.output/'targets.h5','x') as out:
            for ident,g in src.items():
                src.copy(g,out,name=ident);dest=out[ident];states=g['state_indices'][:];n=int(g.attrs['length']);decoded=[]
                for begin in range(0,len(states),4):
                    if time.monotonic()-start>780:raise TimeoutError('Augmentation data cap')
                    selected=states[begin:begin+4];z=torch.from_numpy(g['teacher_z'][begin:begin+4]).cuda();mask=torch.ones(len(z),n,dtype=torch.bool,device='cuda');noise=target_noise([f'{ident}:teacher:{k}' for k in selected],[4*n]*len(z),3,seed=c['spec']['seed'],stream='augmentation_roundtrip',device='cuda')*decoder.fm.scale_ref
                    _,bb=decoder(z,mask,noise=noise,return_backbone=True);x=bb.cpu().numpy();decoded.extend(x)
                    if begin==0:
                        _,again=decoder(z,mask,noise=noise,return_backbone=True);metric=ca_metrics(again[0,:,1].cpu().numpy(),x[0,:,1]);m['controls'].append(dict(target_id=ident,**metric))
                        if metric['ca_rmsd']>.01 or metric['ca_lddt']<.999:raise ValueError('Decoder repeat failed')
                if len(states):
                    decoded=np.asarray(decoded);dest.create_dataset('roundtrip',data=decoded);source=g['teacher_backbone'][:]
                for condition,q in fr['train/'+ident+'/conditions'].items():
                    base=g['conditions/'+condition][:]
                    accepted,rows=qualifying_states(decoded,source,q['fragment'][:],int(q.attrs['start']),base) if len(base) else ([],[])
                    dest.create_dataset('retained/'+condition,data=np.asarray(accepted,dtype=np.int64));m['records'].append(dict(target_id=ident,condition=condition,candidates=rows,retained=len(accepted)))
                out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',targets_sha256=sha(a.output/'targets.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
