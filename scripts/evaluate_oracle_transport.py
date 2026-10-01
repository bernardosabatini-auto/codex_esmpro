"""Decode oracle flow samples as a positive control, never as a predictor."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from train_overfit import score_ensemble
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());prep_path=Path(c['preparation_manifest']);prep=json.loads(prep_path.read_text());label_path=Path(prep['source_manifest']);label=json.loads(label_path.read_text())
    if sha(prep_path)!=c['preparation_manifest_sha256'] or prep['status']!='complete' or sha(label_path)!=prep['source_manifest_sha256'] or sha(prep_path.parent/'endpoints.h5')!=prep['endpoints_sha256'] or sha(label_path.parent/'labels.h5')!=prep['source_labels_sha256']:raise ValueError('oracle provenance mismatch')
    a.output.mkdir(exist_ok=False,parents=True);torch.cuda.set_device(0);torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,scores=[],controls=[],batches=[],scope=prep['scope']);atomic_json(a.output/'manifest.json',m)
    try:
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True);tested=set()
        with torch.no_grad(),inference_precision('fp32'),h5py.File(label_path.parent/'labels.h5') as labels,h5py.File(prep_path.parent/'endpoints.h5') as inputs,h5py.File(a.output/'predictions.h5','x') as output:
            for index,row in enumerate(label['config']['targets']):
                ident=row['id'];n=row['length'];length=row['bucket'];g=labels[ident];record=dict(state=json.loads(g.attrs['state_definition']),teacher_backbone=torch.from_numpy(g['teacher_backbone'][:]),reference_backbone=torch.from_numpy(g['reference_backbone'][:]));mask=(torch.arange(length,device='cuda')[None]<n).repeat(32,1);dn=torch.zeros(32,4*length,3,device='cuda')
                for k in range(32):dn[k,:4*n]=target_noise([ident],[4*n],3,seed=prep['seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                for arm in ('aligned','pca'):
                    for steps in prep['steps']:
                        name=f'collect::oracle::{index}::{arm}::{steps}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                        try:
                            z=torch.zeros(32,length,8,device='cuda');z[:,:n]=torch.from_numpy(inputs[ident][f'{arm}_{steps}'][:]).cuda();_,bb=decoder(z,mask,noise=dn,return_backbone=True);bb=bb[:,:n];scored,_,_=score_ensemble(bb,record)
                            if steps==25 and (length,arm) not in tested:
                                single=decoder(z[:1,:n],mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:,1].cpu().numpy(),single)
                                if control['ca_lddt']<.99 or control['ca_rmsd']>.2:raise ValueError('oracle decoder batching control failed')
                                m['controls'].append(dict(bucket=length,arm=arm,**control));tested.add((length,arm))
                            output.require_group(ident).create_dataset(f'{arm}_{steps}',data=bb.cpu().numpy());m['scores'].append(dict(target_id=ident,arm=arm,steps=steps,**scored));torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                atomic_json(a.output/'manifest.json',m);print('decoded',index+1,'of32',flush=True)
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('oracle decoder audit cap')
        if len(tested)!=8 or len(m['scores'])!=256:raise ValueError('incomplete oracle evaluation')
        m['status']='complete'
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
