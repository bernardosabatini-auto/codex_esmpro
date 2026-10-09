"""Small paired test of the omitted contextual-code output projection."""
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
from context_normalization_profile import project
from generate_fragment_repaint_teacher import generate
from evaluate_decoder_fragment_variance import check_backbones
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_worker(c);parent=c['parent'];a.output.mkdir(exist_ok=False)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],batches=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        model,_=load_legacy(Path(parent['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(parent['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        telemetry=Telemetry(a.output,True)
        codes={arm:np.load(path,allow_pickle=False).reshape(32,4,20,8) for arm,path in parent['codes'].items()}
        lookup={r['id']:r for r in parent['evaluation_rows']}
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out,h5py.File(parent['oracle_predictions']) as oracle,h5py.File(parent['fragments']) as fr:
            for row in c['selected']:
                ident=row['id'];n=row['length'];q=fr['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
                native=oracle['new/'+ident+'/target'][:,st:st+20]
                for arm in ('oracle_original',*c['spec']['arms']):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Normalization profile cap')
                    original=native if arm.startswith('oracle_') else codes[arm][lookup[ident]['index']]
                    # Fixed CPU projection avoids device-dependent rounding in the independently replayed input.
                    target=torch.from_numpy(original)
                    if arm!='oracle_original':target=project(target)
                    torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats()
                    latent,bb,used=generate(model,decoder,ident,n,st,20,target.cuda(),parent['seed'])
                    torch.cuda.synchronize();seconds=time.monotonic()-tick;peak=torch.cuda.max_memory_reserved()/2**30
                    if peak>75 or not np.isfinite(latent).all() or not np.isfinite(bb).all():raise ValueError('Invalid profile output')
                    g=out.create_group(arm+'/'+ident);g['latent']=latent;g['backbone']=bb;g['target']=used
                    if arm.startswith('oracle_'):
                        check=check_backbones(bb,oracle['new/'+ident+'/backbone'][:],q['fragment'][:],st,ident)
                        gap=float(np.max(abs(latent-oracle['new/'+ident+'/latent'][:])))
                        if arm=='oracle_original' and gap>1e-5:raise ValueError('Historical replay failed')
                        m['controls'].append(dict(arm=arm,target_id=ident,latent_max_abs=gap,**check))
                    m['batches'].append(dict(arm=arm,target_id=ident,seconds=seconds,peak_reserved_GiB=peak))
                    out.flush();atomic_json(a.output/'manifest.json',m);print(arm,ident,seconds,flush=True)
        audit_worker(c);m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
