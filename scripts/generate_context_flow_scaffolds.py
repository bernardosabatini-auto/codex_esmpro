"""Use independently sampled contextual codes; keep the scaffold generator frozen."""
import argparse
import json
import time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.precision import inference_precision
from context_flow_generation import audit_worker
from generate_fragment_repaint_teacher import generate
from evaluate_decoder_fragment_variance import check_backbones
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_worker(c);a.output.mkdir(exist_ok=False)
    tick=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],batches=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        telemetry=Telemetry(a.output,True)
        codes={arm:np.load(path,allow_pickle=False).reshape(32,4,20,8) for arm,path in c['codes'].items()}
        lookup={r['id']:r for r in c['evaluation_rows']}
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            with h5py.File(c['oracle_predictions']) as old,h5py.File(c['fragments']) as fr:
                for bucket in (128,256,384,512):
                    row=next(r for r in c['selected'] if r['bucket']==bucket);ident=row['id'];n=row['length']
                    q=fr['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
                    target=old['new/'+ident+'/target'][0,st:st+20]
                    z,bb,_=generate(model,decoder,ident,n,st,20,torch.from_numpy(target).cuda(),c['seed'])
                    gap=float(np.max(abs(z-old['new/'+ident+'/latent'][:])))
                    check=check_backbones(bb,old['new/'+ident+'/backbone'][:],q['fragment'][:],st,ident)
                    if gap>1e-5:raise ValueError('Original oracle latent replay failed')
                    g=out.create_group('controls/'+ident);g['latent']=z;g['backbone']=bb
                    m['controls'].append(dict(target_id=ident,latent_max_abs=gap,**check))
            # Original full targets are now closed; only learned code arrays enter new generation.
            for arm in c['spec']['arms']:
                for row in c['selected']:
                    if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Generation work cap')
                    ident=row['id'];q=lookup[ident];target=codes[arm][q['index']]
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();start=time.monotonic()
                    latent,bb,used=generate(model,decoder,ident,row['length'],q['start'],20,
                                           torch.from_numpy(target).cuda(),c['seed'])
                    torch.cuda.synchronize();seconds=time.monotonic()-start;peak=torch.cuda.max_memory_reserved()/2**30
                    if peak>75 or not np.isfinite(latent).all() or not np.isfinite(bb).all():raise ValueError('Invalid generation')
                    g=out.create_group(arm+'/'+ident);g['latent']=latent;g['backbone']=bb;g['target']=used
                    m['batches'].append(dict(arm=arm,target_id=ident,seconds=seconds,peak_reserved_GiB=peak))
                    out.flush();atomic_json(a.output/'manifest.json',m);print(arm,ident,seconds,flush=True)
        audit_worker(c)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
