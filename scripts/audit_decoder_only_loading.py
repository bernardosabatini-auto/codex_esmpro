"""CPU state/output equivalence; separate fresh processes supply load timings."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import torch
from latentfold.decoder import load_proteinae,load_proteinae_decoder_only
from prepare_overfit import sha


def digest(state):
    h=hashlib.sha256()
    for k,v in sorted(state.items()):h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--checkout',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--child',choices=['full','decoder_only']);a=p.parse_args()
    torch.set_num_threads(2);torch.manual_seed(12);torch.use_deterministic_algorithms(True)
    if a.child:
        tick=time.monotonic();fn=load_proteinae if a.child=='full' else load_proteinae_decoder_only
        model=fn(a.checkout,a.checkpoint,steps=3);elapsed=time.monotonic()-tick
        controls={};rng=torch.Generator().manual_seed(2026100921)
        with torch.no_grad():
            for batch,n,padded in [(1,32,False),(2,64,True)]:
                z=torch.nn.functional.layer_norm(torch.randn(batch,n,8,generator=rng),(8,))
                mask=torch.ones(batch,n,dtype=torch.bool)
                if padded:mask[-1,50:]=False
                z=z*mask[...,None];noise=torch.randn(batch,4*n,3,generator=rng)*model.fm.scale_ref
                _,bb=model(z,mask,noise=noise,return_backbone=True)
                if not torch.isfinite(bb).all():raise ValueError('Nonfinite CPU decoder control')
                controls[f'{batch}_{n}']=bb
        torch.save(dict(mode=a.child,load_seconds=elapsed,state_hash=digest(model.decoder.state_dict()),controls=controls,
                        target_pred=model.target_pred,scale_ref=model.fm.scale_ref,n_steps=model.n_steps),a.output)
        print(a.child,elapsed,flush=True);return
    a.output.mkdir(exist_ok=False)
    for mode in ('full','decoder_only'):
        subprocess.run([sys.executable,str(Path(__file__).resolve()),'--checkout',str(a.checkout),'--checkpoint',str(a.checkpoint),
                        '--output',str(a.output/(mode+'.pt')),'--child',mode],check=True,timeout=240,env=dict(os.environ,CUDA_VISIBLE_DEVICES=''))
    full,slim=[torch.load(a.output/(mode+'.pt'),map_location='cpu',weights_only=True) for mode in ('full','decoder_only')]
    if any(full[k]!=slim[k] for k in ('state_hash','target_pred','scale_ref','n_steps')):raise ValueError('Decoder state/settings differ')
    gaps={k:float((v-slim['controls'][k]).abs().max()) for k,v in full['controls'].items()}
    if any(v!=0 for v in gaps.values()):raise ValueError('CPU outputs are not exact')
    source=Path(__file__).resolve().parents[1]/'src/latentfold/decoder.py'
    d=dict(status='complete',qualified=True,checkpoint=str(a.checkpoint.resolve()),checkpoint_sha256=sha(a.checkpoint),
           decoder_source=str(source),decoder_source_sha256=sha(source),state_sha256=full['state_hash'],cpu_output_max_abs=gaps,
           load_seconds={k:v['load_seconds'] for k,v in [('full',full),('decoder_only',slim)]},
           scope='Exact CPU state/settings/output controls. Timings are fresh processes on the same login host, not a controlled GPU-node speed benchmark. Historical GPU oracle replay remains required.')
    (a.output/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))


if __name__=='__main__':main()
