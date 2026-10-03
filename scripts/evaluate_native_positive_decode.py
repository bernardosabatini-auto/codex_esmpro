import argparse
import json
import time
from pathlib import Path
import h5py
import torch
from latentfold.decoder import load_proteinae
from latentfold.native_anchors import decode_native_anchors
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from native_positive_coverage import audit_generation
from prepare_overfit import sha
from profile_gpu import atomic_json,Telemetry


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec=audit_generation(c);a.output.mkdir(exist_ok=False);start=time.monotonic()
    m=dict(status='running',config=c,native_controls=[],historical_controls=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m);telemetry=None
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);telemetry=Telemetry(a.output,True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as fr,h5py.File(c['profile_predictions']) as old,h5py.File(a.output/'predictions.h5','x') as out:
            for ident in c['control_ids']:
                latent=torch.from_numpy(fr['train/'+ident+'/reference_z'][:]).cuda();z,bb=decode_native_anchors(decoder,latent,target_id=ident,seed=c['historical_seed']);bb=bb.cpu().numpy()
                metrics=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,old['native/'+ident+'/backbone'][:])]
                row=dict(target_id=ident,max_ca_rmsd=max(x['ca_rmsd'] for x in metrics),min_ca_lddt=min(x['ca_lddt'] for x in metrics))
                if row['max_ca_rmsd']>.2 or row['min_ca_lddt']<.99:raise ValueError('Historical decoder control failed')
                m['historical_controls'].append(row);g=out.create_group('historical/'+ident);g.create_dataset('latent',data=z.cpu().numpy());g.create_dataset('backbone',data=bb)
            for ident in c['target_ids']:
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Native decode work cap')
                latent=torch.from_numpy(fr['train/'+ident+'/reference_z'][:]).cuda();torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                z,bb=decode_native_anchors(decoder,latent,target_id=ident,seed=spec['native_seed']);_,repeat=decode_native_anchors(decoder,latent,target_id=ident,seed=spec['native_seed']);torch.cuda.synchronize()
                error=float((bb-repeat).abs().max());peak=torch.cuda.max_memory_reserved()/2**30
                if error>1e-4 or peak>75:raise ValueError('Native repeat/resource control failed')
                g=out.create_group('native/'+ident);g.create_dataset('latent',data=z.cpu().numpy());g.create_dataset('backbone',data=bb.cpu().numpy());g.create_dataset('same_batch_repeat',data=repeat.cpu().numpy())
                m['native_controls'].append(dict(target_id=ident,coordinate_max_abs=error,peak_reserved_GiB=peak,seconds=time.monotonic()-tick));out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
