"""Cross frozen flow latents with decoder noises; never change the generator."""
import argparse
import json
import time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from latentfold.precision import inference_precision
from decoder_fragment_variance_core import audit
from fragment_validation_core import raw_rows
from prepare_overfit import sha
from profile_gpu import atomic_json,Telemetry


def check_backbones(actual,expected,fragment,start,ident):
    scores=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(actual,expected)]
    left=raw_rows(actual,fragment,start,'control',ident,ident);right=raw_rows(expected,fragment,start,'control',ident,ident)
    row=dict(max_ca_rmsd=max(r['ca_rmsd'] for r in scores),min_ca_lddt=min(r['ca_lddt'] for r in scores),same_decisions=all(x[k]==y[k] for x,y in zip(left,right) for k in ('coarse_valid','raw_gate_passed')))
    if row['max_ca_rmsd']>.2 or row['min_ca_lddt']<.99 or not row['same_decisions']:raise ValueError('Decoder parity control failed: '+ident)
    return row


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec=audit(c);a.output.mkdir(exist_ok=False);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],timing=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);telemetry=Telemetry(a.output,True)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as fr,h5py.File(c['baseline_predictions']) as old,h5py.File(a.output/'predictions.h5','x') as out:
            for source in c['selected']:
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Crossed decoder work cap')
                ident=source['id'];n=source['length'];q=fr['train/'+ident+'/conditions/c20_center'];fragment=q['fragment'][:];st=int(q.attrs['start'])
                z=torch.from_numpy(old['new/'+ident+'/latent'][:]).cuda();native=torch.from_numpy(fr['train/'+ident+'/reference_z'][:]).cuda()
                if z.shape!=(4,n,8) or native.shape!=(n,8) or not torch.isfinite(z).all() or not torch.isfinite(native).all():raise ValueError('Invalid fixed latent input')
                mask=torch.ones(4,n,dtype=torch.bool,device='cuda');noise=[target_noise([ident],[4*n],3,seed=spec['seed'],sample_index=k,stream=spec['decoder_stream'],device='cuda')*decoder.fm.scale_ref for k in range(5)]
                torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();generated=[]
                for eps in noise:
                    _,bb=decoder(z,mask,noise=eps.expand(4,-1,-1),return_backbone=True);generated.append(bb.cpu().numpy())
                generated=np.stack(generated,axis=1)
                _,first=decoder(native[None].expand(4,-1,-1),mask,noise=torch.cat(noise[:4]),return_backbone=True)
                _,last=decoder(native[None],mask[:1],noise=noise[4],return_backbone=True)
                natives=torch.cat([first,last]).cpu().numpy()
                _,single=decoder(native[None],mask[:1],noise=noise[0],return_backbone=True);single=single.cpu().numpy()
                torch.cuda.synchronize();peak=torch.cuda.max_memory_reserved()/2**30
                if peak>75:raise ValueError('Decoder memory profile failed')
                diagonal=np.stack([generated[k,k] for k in range(4)])
                m['controls'].append(dict(kind='historical',target_id=ident,**check_backbones(diagonal,old['new/'+ident+'/backbone'][:],fragment,st,ident)))
                m['controls'].append(dict(kind='native_batch',target_id=ident,**check_backbones(single,natives[:1],fragment,st,ident)))
                g=out.create_group('generated/'+ident);g['latent']=z.cpu().numpy();g['backbone']=generated
                g=out.create_group('native/'+ident);g['latent']=native.cpu().numpy();g['backbone']=natives;g['single_backbone']=single[0]
                m['timing'].append(dict(target_id=ident,length=n,seconds=time.monotonic()-tick,peak_reserved_GiB=peak));out.flush();atomic_json(a.output/'manifest.json',m);print('decoded',ident,flush=True)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
