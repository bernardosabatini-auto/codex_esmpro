"""One short RTX preflight; preserve frame failures before any iteration."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.precision import inference_precision
from compatible_fragment_core import encoder
from context_refresh_frame_core import audit,frame_metrics,frame_gate
from native_anchor_training_core import state_hash
from profile_gpu import Telemetry,atomic_json
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser()
    for k in ('source','config','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());gc,parent=audit(c,full=False);b=c['base']
    a.output.mkdir(exist_ok=False);tick=time.monotonic();telemetry=None
    m=dict(status='running',config=c,rows=[],controls=[],timing=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        codec=load_proteinae(a.source/'ProteinAE_v1',Path(b['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        def hashes():return dict(encoder=state_hash(codec.ae_model.encoder.state_dict()),decoder=state_hash(codec.decoder.state_dict()))
        m['initial_weights']=hashes()
        if m['initial_weights']['decoder']!=parent['frozen_original']:raise ValueError('Changed original decoder')
        telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(b['source_predictions']) as prior, \
             h5py.File(b['noise_source']) as noises,h5py.File(a.output/'predictions.h5','x') as out:
            for row in c['selected']:
                ident=row['id'];mask=torch.ones(4,row['length'],dtype=torch.bool,device='cuda')
                noise=torch.from_numpy(noises['noise/'+ident][:]).cuda();out['noise/'+ident]=noise.cpu().numpy()
                for arm in ('parent','native_direct'):
                    if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Encoder-frame work cap')
                    reference=prior[arm+'/'+ident+'/backbone'][:];bb=torch.from_numpy(reference).cuda()
                    old=torch.from_numpy(prior[arm+'/'+ident+'/latent'][:]).cuda()
                    replay=codec(old,mask,noise=noise,return_backbone=True)[1]
                    g=out.create_group(arm+'/'+ident);g['original_replay']=replay.cpu().numpy()
                    error=float(np.max(np.abs(replay.cpu().numpy()-reference)))
                    m['controls'].append(dict(arm=arm,target_id=ident,max_abs=error))
                    if error>1e-5:raise ValueError('Archived original-decoder replay changed')
                    centered=bb-bb.mean((1,2),keepdim=True);g['input']=centered.cpu().numpy()
                    torch.cuda.synchronize();started=time.monotonic();latent=encoder(codec,centered)
                    rebuilt=codec(latent,mask,noise=noise,return_backbone=True)[1];torch.cuda.synchronize()
                    m['timing'].append(dict(arm=arm,target_id=ident,seconds=time.monotonic()-started))
                    g['latent']=latent.cpu().numpy();g['backbone']=rebuilt.cpu().numpy()
                    m['rows'].extend(dict(r,arm=arm,target_id=ident,bucket=row['bucket']) for r in frame_metrics(rebuilt.cpu().numpy(),reference))
                out.flush();atomic_json(a.output/'manifest.json',m);print('frame',ident,flush=True)
        m['final_weights']=hashes();m['peak_reserved_GiB']=torch.cuda.max_memory_reserved()/2**30
        if m['initial_weights']!=m['final_weights'] or m['peak_reserved_GiB']>75:raise ValueError('Changed weights or exceeded memory')
        audit(c,full=False)
        m.update(status='complete',frame_qualified=frame_gate(m['rows']),predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
