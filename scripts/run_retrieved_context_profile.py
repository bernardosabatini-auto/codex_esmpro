"""Transfer actual training-code windows and preserve separate native controls."""
import argparse
import json
import os
import tempfile
import time
from pathlib import Path
IMPORT_START=time.monotonic()
import h5py
import numpy as np
import torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.precision import inference_precision
from context_flow_generation import audit_worker
from generate_fragment_repaint_teacher import generate
from evaluate_decoder_fragment_variance import check_backbones
from local_checkpoint import stage_checkpoint
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_worker(c);parent=c['parent'];a.output.mkdir(exist_ok=False)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],batches=[],training_updates_executed=0,
        import_seconds=time.monotonic()-IMPORT_START,phases={})
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        telemetry=Telemetry(a.output,True)
        m['phases']['cuda_and_telemetry_seconds']=time.monotonic()-start
        # Sequential verified copies avoid mmap page faults against shared storage.
        # The local files are private to this job; original dependencies remain untouched.
        with tempfile.TemporaryDirectory(prefix='esm-retrieval-',dir=os.environ.get('SLURM_TMPDIR') or '/tmp') as local:
            tick=time.monotonic();checkpoint=stage_checkpoint(c['checkpoint'],c['sources'],Path(local)/'flow')
            decoder_checkpoint=stage_checkpoint(c['decoder_checkpoint'],c['sources'],Path(local)/'decoder')
            m['phases']['local_staging_seconds']=time.monotonic()-tick;tick=time.monotonic()
            model,_=load_legacy(checkpoint,trusted_pickle=True);model.cuda().eval().requires_grad_(False)
            m['phases']['generator_load_seconds']=time.monotonic()-tick;tick=time.monotonic()
            decoder=load_proteinae(a.source/'ProteinAE_v1',decoder_checkpoint,steps=3).cuda().eval().requires_grad_(False)
            m['phases']['decoder_load_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)
            with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out,h5py.File(c['inputs']) as inputs,h5py.File(c['oracle_predictions']) as oracle,h5py.File(c['fragments']) as queries:
                for row in c['selected']:
                    ident=row['id'];n=row['length'];q=queries['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
                    for arm in ('oracle_original',*c['spec']['arms'],'donor_self'):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Retrieval profile cap')
                        name,length,offset=ident,n,st
                        if arm=='oracle_original':target=oracle['new/'+ident+'/target'][:,st:st+20]
                        elif arm=='donor_self':
                            donor=c['donors'][ident]['retrieved'][0];name,length,offset=donor['id'],donor['length'],donor['start']
                            target=inputs[ident+'/retrieved'][0]
                        else:target=inputs[ident+'/'+arm][:]
                        torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats()
                        latent,bb,used=generate(model,decoder,name,length,offset,20,torch.from_numpy(target).cuda(),parent['seed'])
                        torch.cuda.synchronize();seconds=time.monotonic()-tick;peak=torch.cuda.max_memory_reserved()/2**30
                        if peak>75 or not np.isfinite(latent).all() or not np.isfinite(bb).all():raise ValueError('Invalid retrieval profile output')
                        g=out.create_group(arm+'/'+ident);g['latent']=latent;g['backbone']=bb;g['target']=used
                        if arm=='oracle_original':
                            check=check_backbones(bb,oracle['new/'+ident+'/backbone'][:],q['fragment'][:],st,ident)
                            gap=float(np.max(abs(latent-oracle['new/'+ident+'/latent'][:])))
                            if gap>1e-5:raise ValueError('Historical checkpoint/sampler parity failed')
                            m['controls'].append(dict(target_id=ident,latent_max_abs=gap,**check))
                        m['batches'].append(dict(arm=arm,target_id=ident,seconds=seconds,peak_reserved_GiB=peak))
                        out.flush();atomic_json(a.output/'manifest.json',m);print(arm,ident,seconds,flush=True)
        audit_worker(c);m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
