"""Validate selected ESMC layers and profile four length buckets before caching."""
import argparse,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.data import read_record
from latentfold.embedding import FinalESMC
from predict import file_identity
from profile_gpu import atomic_json,Telemetry


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());path=Path(c['targets'])
    if hashlib.sha256(path.read_bytes()).hexdigest()!=c['targets_sha256']:raise ValueError('changed target manifest')
    targets=json.loads(path.read_text())['targets'];a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);started=time.monotonic()
    m=dict(status='running',config=c,controls=[],batches=[],completed_targets=0,scope='16 training structures; extraction calibration, not layer-quality selection',precision='FP32',layer_convention='20/40/60 post-block residual stream; 80 after final model normalization');telemetry=None
    atomic_json(a.output/'manifest.json',m)
    try:
        e=FinalESMC(a.source/'data/esmc6b',precision='fp32')
        m['artifacts']=[file_identity(p,hash_contents=True) for p in sorted((a.source/'data/esmc6b').glob('*')) if p.suffix in ('.json','.safetensors')]
        records=[read_record(t['file'],t['split'],t['id'],embedding_dim=2560) for t in targets]
        telemetry=Telemetry(a.output,True)
        with h5py.File(a.output/'embeddings.h5','x') as output:
            for length,batch in ((128,32),(256,16),(384,8),(512,8)):
                group=[r for r in records if next(b for b in (128,256,384,512) if len(r['sequence'])<=b)==length]
                if len(group)!=4:raise ValueError('expected four calibration proteins per bucket')
                sequences=[group[i%4]['sequence'] for i in range(batch)]
                selected=e(sequences,length,layers=(20,40,60,80));ordinary=e(sequences,length)
                delta=float((selected[80]-ordinary).abs().max());control=dict(length=length,batch=batch,final_layer_max_abs=delta);m['controls'].append(control)
                if delta>1e-6:raise ValueError('selected extraction changed final embedding')
                for i,r in enumerate(group):
                    g=output.create_group(r['id']);g.attrs['sequence_sha256']=r['sequence_sha256'];g.create_dataset('cached_z',data=r['z'].numpy())
                    for k in (20,40,60,80):g.create_dataset(f'layer{k}',data=selected[k][i,:len(r['sequence'])].cpu().numpy())
                    m['completed_targets']+=1
                del ordinary,selected
                for repeat in range(3):
                    if time.monotonic()-started>720:raise TimeoutError('12 minute work cap')
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();nvtx=f'collect::layers::{length}::{repeat}'
                    torch.cuda.nvtx.range_push(nvtx)
                    try:
                        values=e(sequences,length,layers=(20,40,60,80));host={k:v.cpu().numpy() for k,v in values.items()};torch.cuda.synchronize();seconds=time.monotonic()-tick
                    finally:torch.cuda.nvtx.range_pop()
                    m['batches'].append(dict(nvtx_range=nvtx,length=length,batch=batch,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    del values,host
                output.flush();atomic_json(a.output/'manifest.json',m);print('layers bucket',length,'complete',flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-started;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
