"""Fresh-noise paired reconstruction check under an explicit revised protocol."""
import argparse,json,time
from pathlib import Path
import h5py,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from calibrate_fragment_frame import scores
from prepare_overfit import sha
from profile_gpu import atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','data_manifest','data_report','calibration_report','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed confirmation source')
    protocol=json.loads(Path(c['protocol']).read_text())
    if c['seeds']!=protocol['seeds']:raise ValueError('Undeclared decoder seeds')
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic();m=dict(status='running',config=c,records=[]);atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['fragments']) as src,h5py.File(a.output/'reconstructions.h5','x') as out:
            for ident,g in src['train'].items():
                raw=g['reference_backbone'][:];n=len(raw);mask=torch.ones(1,n,dtype=torch.bool,device='cuda');original=torch.from_numpy(g['reference_z'][:])[None].cuda()
                for condition,q in g['conditions'].items():
                    anchored=torch.from_numpy(q['target_latent'][:])[None].cuda();args=(raw,q['fragment'][:],int(q.attrs['start']))
                    for seed in c['seeds']:
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Frame confirmation cap')
                        noise=target_noise([ident],[4*n],3,seed=seed,stream='frame_confirmation:'+condition,device='cuda')*decoder.fm.scale_ref
                        row=dict(target_id=ident,condition=condition,seed=seed)
                        for arm,z in [('original',original),('anchored',anchored)]:
                            _,bb=decoder(z,mask,noise=noise.clone(),return_backbone=True);bb=bb[0].cpu().numpy();out.create_dataset(f'{ident}/{condition}/{seed}/{arm}',data=bb);row[arm]=scores(bb,*args)
                        m['records'].append(row)
                out.flush();atomic_json(a.output/'manifest.json',m)
        m.update(status='complete',predictions_sha256=sha(a.output/'reconstructions.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
