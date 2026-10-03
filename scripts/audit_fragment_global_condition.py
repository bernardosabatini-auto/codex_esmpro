"""Measure fragment-induced global modulation on a fixed training-only panel."""
import argparse
import json
from pathlib import Path

import h5py
import numpy as np
import torch
from torch.nn import functional as F

from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.model import timestep_embedding
from prepare_overfit import sha


HEADS = dict(parent6000='50106855', full512='50127267', full7941='50127352',
             frozen512='50139079', frozen7941='50139147')
TIMES = (.05, .25, .5, .75, .95)


def linear(x, state, prefix):
    return F.linear(x, state[prefix+'.weight'], state[prefix+'.bias'])


def rms(x):
    return x.square().mean(-1).sqrt()


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];sources={};ids=[]
    for jid in ('50134308','50134476','50134622','50134771'):
        path=root/f'runs/fragment_source_refold_{jid}/manifest.json';m=json.loads(path.read_text())
        if m['status']!='complete':raise ValueError('Incomplete training source inventory')
        sources[str(path)]=sha(path)
        ids.extend(r['target_id'] for r in m['config']['entries'] if r['arm']=='original512')
    if len(ids)!=64 or len(set(ids))!=64:raise ValueError('Changed fixed training inventory')
    corpus=root/'runs/broad_fragment_corpora_20261003/control512/fragments.h5'
    sources[str(corpus)]=sha(corpus);items=[]
    with h5py.File(corpus) as f:
        if not set(ids)<=set(f['train']) or set(ids)&set(f['development']):raise ValueError('Not training-only')
        for ident in sorted(ids):
            g=f['train/'+ident];q=g['conditions/c20_center'];n=int(g.attrs['length'])
            features,keep=fragment_features(torch.from_numpy(q['latent'][:]),q.attrs['sequence'],length=n,start=int(q.attrs['start']))
            items.append(dict(id=ident,length=n,features=features,keep=keep))
    records=[];torch.set_num_threads(2)
    with torch.no_grad():
        for name,jid in HEADS.items():
            path=root/f'runs/fragment_training_{jid}/ema_2000.ckpt';sources[str(path)]=sha(path)
            ck=torch.load(path,map_location='cpu',weights_only=False,mmap=True)
            state={k.replace('_orig_mod.',''):v for k,v in ck['ema'].items()};spec=dict(ck['adapter_config']);spec.pop('variant')
            adapter=FragmentGeometryAdapter(**spec).eval();adapter.load_state_dict(ck['fragment_adapter'])
            null=state['null_cond'].reshape(1,-1);dim=null.shape[-1];n_layers=ck['arch']['n_layers']
            pools=[];token_scales=[]
            for item in items:
                mask=torch.ones(1,item['length'],dtype=torch.bool)
                delta=adapter(item['features'][None],item['keep'][None],mask,torch.zeros(1,dtype=torch.bool))[0]
                pools.append(delta.mean(0));token_scales.append(float(rms(delta[item['keep']]).mean()))
            pool=torch.stack(pools)
            for t in TIMES:
                emb=timestep_embedding(torch.full((len(items),),t),dim)
                time=linear(F.silu(linear(emb,state,'t_mlp.0')),state,'t_mlp.2')
                base=time+null;conditioned=base+pool;modulations=[]
                for block in range(n_layers):
                    prefix=f'blocks.{block}.ada.1'
                    baseline=linear(F.silu(base),state,prefix)
                    changed=linear(F.silu(conditioned),state,prefix)
                    modulations.append((rms(changed-baseline)/rms(baseline).clamp_min(1e-12)).numpy())
                output_base=linear(F.silu(base),state,'out_ada.1')
                output_changed=linear(F.silu(conditioned),state,'out_ada.1')
                for k,item in enumerate(items):
                    records.append(dict(arm=name,target_id=item['id'],length=item['length'],time=t,
                                        token_delta_rms=token_scales[k],pool_delta_rms=float(rms(pool[k])),
                                        pool_to_time_rms=float(rms(pool[k])/rms(time[k]).clamp_min(1e-12)),
                                        pool_to_total_null_condition_rms=float(rms(pool[k])/rms(base[k]).clamp_min(1e-12)),
                                        median_block_modulation_relative_change=float(np.median([v[k] for v in modulations])),
                                        max_block_modulation_relative_change=float(max(v[k] for v in modulations)),
                                        output_modulation_relative_change=float(rms(output_changed[k]-output_base[k])/rms(output_base[k]).clamp_min(1e-12))))
            del ck,state,adapter
    summary=[]
    for name in HEADS:
        rows=[r for r in records if r['arm']==name]
        summary.append(dict(arm=name,**{key:float(np.median([r[key] for r in rows])) for key in
                                       ('token_delta_rms','pool_delta_rms','pool_to_time_rms','pool_to_total_null_condition_rms',
                                        'median_block_modulation_relative_change','output_modulation_relative_change')}))
    result=dict(status='complete',sources=sources,records=records,summary=summary,
                scope='CPU only; same64 source-calibration training proteins, central20motifs and five fixed flow times. No development outcomes or refold scores used. Relative modulation changes diagnose routing magnitude, not causality or designability. No checkpoints selected.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Fragment global-conditioning audit','',result['scope'],'',
           '|Arm|Pool delta RMS|Pool/time RMS|Pool/null+time RMS|Median block modulation change|Output modulation change|',
           '|---|---:|---:|---:|---:|---:|']
    for r in summary:
        lines.append('|'+r['arm']+'|'+'|'.join(f"{r[k]:.3f}" for k in ('pool_delta_rms','pool_to_time_rms','pool_to_total_null_condition_rms','median_block_modulation_relative_change','output_modulation_relative_change'))+'|')
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
