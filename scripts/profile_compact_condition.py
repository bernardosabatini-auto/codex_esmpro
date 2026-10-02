"""Paired structural and memory controls for compact single-sequence conditioning."""
import argparse,gc,hashlib,json,time
from contextlib import nullcontext
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


LAYOUTS=(('single_exact',1,False),('single_padded',1,True),('batch8',8,True),('batch32',32,True))


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for field in ('selection','protocol'):
        if sha(c[field])!=c[field+'_sha256']:raise ValueError('changed '+field)
    if len(c['targets'])!=4 or {r['bucket'] for r in c['targets']}!={128,256,384,512}:raise ValueError('four bucket controls required')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
    m=dict(status='running',config=c,micro=[],warmups=[],batches=[],controls=[],training_updates_executed=0,scope='Strict FP32 expanded versus compact conditioner storage; four longest tuning-bucket proteins, two heads. Cached-stage speed/memory only, no full accuracy or end-to-end claim.')
    start=time.monotonic();telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True);torch.manual_seed(c['seed'])
        with torch.no_grad(),inference_precision('fp32'):
            decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
            with h5py.File(c['embedding_cache']) as cache,h5py.File(a.output/'predictions.h5','x') as output:
                for head in c['heads']:
                    if sha(head['checkpoint'])!=head['checkpoint_sha256']:raise ValueError('checkpoint changed')
                    model,_=load_legacy(Path(head['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
                    for record in c['targets']:
                        ident=record['id'];n=record['length'];g=cache['tuning'][ident];embedding=g['80'][:]
                        if g.attrs['sequence_sha256']!=record['sequence_sha256'] or hashlib.sha256(embedding.tobytes()).hexdigest()!=c['embedding_arrays_sha256'][ident]:raise ValueError('embedding changed')
                        results={}
                        for precision in ('fp32','compact'):
                            with nullcontext():
                                for layout,count,padded in LAYOUTS:
                                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('precision probe work cap')
                                    torch.cuda.empty_cache()
                                    length=record['bucket'] if padded else n;esm=torch.zeros(count,length,2560,device='cuda');esm[:,:n]=torch.from_numpy(embedding).cuda();mask=torch.arange(length,device='cuda')[None].expand(count,-1)<n
                                    noise=torch.zeros(count,length,8,device='cuda');dn=torch.zeros(count,4*length,3,device='cuda')
                                    for sample_index in range(count):
                                        noise[sample_index,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=sample_index,device='cuda')[0]
                                        dn[sample_index,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=sample_index,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                                    def predict():
                                        z=sample(model,esm,mask,SampleConfig(steps=25,guidance=head['guidance']),noise=noise,conditioning_ids=[ident]*count,compact_condition=precision=='compact')
                                        _,bb=decoder(z,mask,noise=dn,return_backbone=True)
                                        return bb[:,:n].cpu().numpy()
                                    torch.cuda.synchronize();tick=time.monotonic();predict();torch.cuda.synchronize()
                                    m['warmups'].append(dict(head=head['name'],target_id=ident,precision=precision,layout=layout,seconds=time.monotonic()-tick))
                                    for repeat in range(3):
                                        label=f"collect::compact::{head['name']}::{ident}::{precision}::{layout}::{repeat}";torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(label)
                                        try:bb=predict();torch.cuda.synchronize();seconds=time.monotonic()-tick
                                        finally:torch.cuda.nvtx.range_pop()
                                        if not np.isfinite(bb).all():raise ValueError('nonfinite generated backbone')
                                        m['batches'].append(dict(head=head['name'],target_id=ident,bucket=record['bucket'],precision=precision,layout=layout,repeat=repeat,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),peak_allocated_bytes=torch.cuda.max_memory_allocated(),nvtx_range=label))
                                    results[precision,layout]=bb;output.require_group(head['name']+'/'+ident+'/'+precision).create_dataset(layout,data=bb)
                                    if layout!='single_exact':m['controls'].append(dict(head=head['name'],target_id=ident,precision=precision,layout=layout,kind='batching',samples=1,**ca_metrics(bb[0,:,1],results[precision,'single_exact'][0,:,1])))
                                    del esm,mask,noise,dn;atomic_json(a.output/'manifest.json',m)
                        for layout,count,_ in LAYOUTS:
                            pairs=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(results['compact',layout],results['fp32',layout])]
                            m['controls'].append(dict(head=head['name'],target_id=ident,precision='compact',layout=layout,kind='arithmetic',samples=count,ca_rmsd=max(r['ca_rmsd'] for r in pairs),ca_lddt=min(r['ca_lddt'] for r in pairs)))
                        output.flush();atomic_json(a.output/'manifest.json',m);print('profiled',head['name'],ident,flush=True)
                    del model;gc.collect();torch.cuda.empty_cache()
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
