"""Test preservation of held development conformations through ProteinAE."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.backbone import encode_backbone
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from predict import file_identity
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());panel=Path(c['panel'])
    if hashlib.sha256(panel.read_bytes()).hexdigest()!=c['panel_sha256']:raise ValueError('changed panel')
    rows=[r for r in json.loads(panel.read_text())['development'] if r['category']!='md_emulation']
    if len(rows)!=16:raise ValueError('expected sixteen development multistate proteins')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    start=time.monotonic();m=dict(status='running',config=c,targets=[],batches=[],controls=[],precision='strict FP32');telemetry=None
    atomic_json(a.output/'manifest.json',m)
    try:
        checkpoint=a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt';m['checkpoint']=file_identity(checkpoint,hash_contents=True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',checkpoint).cuda().eval();telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as output:
            for index,row in enumerate(rows):
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('experiment work cap reached')
                n=len(row['sequence']);g=output.create_group(str(index));g.attrs['target_id']=row['query_id'];g.attrs['family']=row['family']
                g.create_dataset('common_indices',data=row['common_indices'])
                noise=torch.cat([target_noise([row['query_id']],[4*n],3,seed=c['seed'],sample_index=k,stream='decoder',device='cuda') for k in range(8)])*decoder.fm.scale_ref
                for ref_index,ref in enumerate(row['references']):
                    if hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()!=ref['sha256']:raise ValueError('reference changed')
                    positions=ref['observed_indices'];mask=torch.zeros(1,n,dtype=torch.bool,device='cuda');mask[:,positions]=True
                    bb=torch.zeros(1,n,4,3,device='cuda');bb[:,positions]=torch.tensor(ref['backbone'],device='cuda')
                    z=encode_backbone(decoder,bb,mask);r=g.create_group(str(ref_index));r.create_dataset('reference_backbone',data=bb[0].cpu().numpy());r.create_dataset('mask',data=mask[0].cpu().numpy());r.create_dataset('z',data=z[0].cpu().numpy())
                    for steps in (3,10):
                        decoder.n_steps=steps;torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                        name=f'collect::state_roundtrip::{index}::{ref_index}::{steps}';torch.cuda.nvtx.range_push(name)
                        try:
                            _,pred=decoder(z.repeat(8,1,1),mask.repeat(8,1),return_backbone=True,noise=noise)
                            pred=pred.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=name,seconds=seconds,length=n,batch=8,steps=steps,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        if ref_index==0:
                            single=decoder(z,mask,noise=noise[:1])[0].cpu().numpy()
                            control=ca_metrics(pred[0,positions,1],single[positions]);m['controls'].append(dict(target_id=row['query_id'],steps=steps,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('batch control failed')
                        r.create_dataset(f'steps{steps}',data=pred)
                m['targets'].append(dict(id=row['query_id'],family=row['family'],length=n,references=len(row['references'])));output.flush();atomic_json(a.output/'manifest.json',m)
                print('experimental state roundtrip',index+1,'of',len(rows),flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
