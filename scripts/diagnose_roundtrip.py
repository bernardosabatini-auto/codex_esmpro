"""Calibrate true backbone encoding and paired decoder seeds on mapped training data."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import h5py
import numpy as np
import torch
from latentfold.backbone import mapped_backbone, encode_backbone
from latentfold.data import read_record
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from predict import file_identity
from profile_gpu import Telemetry, atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    target_path=Path(c['targets'])
    if hashlib.sha256(target_path.read_bytes()).hexdigest()!=c['targets_sha256']:raise ValueError('changed targets')
    targets=json.loads(target_path.read_text())['targets']
    if len(targets)!=16 or any(t['split']!='train' for t in targets):raise ValueError('expected 16 calibration training targets')
    a.output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    m=dict(status='running',scope='training adapter calibration, not ensemble benchmark',config=c,targets=[],batches=[],controls=[],precision='strict FP32')
    atomic_json(a.output/'manifest.json',m);telemetry=None
    try:
        checkpoint=a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt'
        m['checkpoint']=file_identity(checkpoint,hash_contents=True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',checkpoint).cuda().eval()
        telemetry=Telemetry(a.output,True)
        with h5py.File(a.output/'predictions.h5','x') as output, torch.no_grad(), inference_precision('fp32'):
            for index,meta in enumerate(targets):
                if time.monotonic()-started>720:raise TimeoutError('12 minute diagnostic cap')
                record=read_record(meta['file'],meta['split'],meta['id'],embedding_dim=2560)
                if record['sequence_sha256']!=meta['sequence_sha256']:raise ValueError('sequence changed')
                bb=mapped_backbone(meta['source_pdb'],meta['residue_map']);n=len(bb)
                alignment=ca_metrics(bb[:,1],record['ca'].numpy())
                if alignment['ca_rmsd']>.02:raise ValueError('source coordinates differ from cached CA')
                mask=torch.ones(1,n,device='cuda',dtype=torch.bool)
                fresh=encode_backbone(decoder,torch.from_numpy(bb[None]).cuda(),mask)
                if index==0:
                    # Compare against the external implementation's own coordinate extraction.
                    coords=torch.zeros(1,n,37,3,device='cuda');coords[:,:, [0,1,2,4]]=torch.from_numpy(bb[None]).cuda()
                    atom_mask=torch.zeros_like(coords,dtype=torch.bool);atom_mask[:,:, [0,1,2,4]]=True
                    ae=decoder.ae_model;rotation=ae.cfg_exp.model.augmentation.global_rotation
                    ae.cfg_exp.model.augmentation.global_rotation=False
                    try:x,rm,cm,*_=ae.extract_clean_sample(dict(coords=coords,mask_dict=dict(coords=atom_mask)))
                    finally:ae.cfg_exp.model.augmentation.global_rotation=rotation
                    direct=ae.encoder(dict(x_1=ae.fm._mask_and_zero_com(x,cm),mask=rm,coords_mask=cm))['single_repr']
                    delta=float((fresh-direct).abs().max());m['controls'].append(dict(kind='official_encoder_path',max_abs=delta))
                    if delta>1e-6:raise ValueError('encoder adapter does not match official path')
                cached=record['z'][None].cuda()
                group=output.create_group(str(index));group.attrs['target_id']=meta['id'];group.create_dataset('reference_backbone',data=bb)
                group.create_dataset('fresh_z',data=fresh.cpu().numpy());group.create_dataset('cached_z',data=cached.cpu().numpy())
                m['targets'].append(dict(id=meta['id'],length=n,source_pdb=file_identity(Path(meta['source_pdb']),hash_contents=True),source_alignment=alignment,latent_rmse=float((fresh-cached).square().mean().sqrt())))
                noise=torch.cat([target_noise([meta['id']],[4*n],3,seed=c['seed'],sample_index=k,stream='decoder',device='cuda') for k in range(8)])*decoder.fm.scale_ref
                for label,z in (('fresh',fresh),('cached',cached)):
                    for steps in (3,10):
                        decoder.n_steps=steps
                        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                        nvtx=f'collect::roundtrip::{index}::{label}::{steps}';torch.cuda.nvtx.range_push(nvtx)
                        try:
                            ca,pred=decoder(z.repeat(8,1,1),mask.repeat(8,1),return_backbone=True,noise=noise)
                            pred=pred.cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                        finally:torch.cuda.nvtx.range_pop()
                        m['batches'].append(dict(nvtx_range=nvtx,seconds=seconds,length=n,batch=8,latent=label,steps=steps,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                        if index in (0,4,8,12) and label=='fresh':
                            single=decoder(z,mask,noise=noise[:1])[0].cpu().numpy()
                            control=ca_metrics(pred[0,:,1],single);m['controls'].append(dict(kind='batch_vs_single',length=n,steps=steps,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('roundtrip batch control failed')
                        group.create_dataset(f'{label}_steps{steps}',data=pred)
                        del ca
                output.flush();atomic_json(a.output/'manifest.json',m);print('roundtrip target',index+1,'of',len(targets),flush=True)
        m['status']='complete'
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-started;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
