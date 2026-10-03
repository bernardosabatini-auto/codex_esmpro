"""Audit frozen weights, exact labels, numerical controls and saved predictions."""
import argparse
import json
import math
from pathlib import Path
import h5py
import numpy as np
import torch
from native_anchor_training_core import audit,load_pairs,state_hash,tensor_hash
from extra_fragment_validation_core import load_conditions
from fragment_validation_core import raw_rows
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),profile_qualified=False)
    c=m['config'];spec,labels=audit(c);data=load_pairs(c);count=c['updates'];active=sorted({r['bucket'] for r in labels['rows']})
    if m['updates']!=count or len(m['training'])!=count or m['active_buckets']!=active or len(m['controls'])!=16 or [r['step'] for r in m['evaluations']]!=[0,count]:raise ValueError('Changed training/evaluation inventory')
    if not math.isfinite(m['peak_reserved_GiB']) or m['peak_reserved_GiB']>75 or m['generator_initial']!=m['generator_final'] or m['reference_initial']!=m['reference_final'] or m['adapter_initial']==m['adapter_final']:raise ValueError('Frozen weights, update or resource check failed')
    for step,row in enumerate(m['training']):
        length=active[step%len(active)];batch=spec['batches'][str(length)];factor=min((step+1)/spec['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
        if row['step']!=step+1 or row['length']!=length or row['batch']!=batch or len(row['ids'])!=batch or row['learning_rate_factor']!=factor:raise ValueError('Changed draw/schedule')
        if any(i not in data or data[i]['bucket']!=length for i in row['ids']):raise ValueError('Unqualified training example')
        positive=torch.zeros(batch,length,8);negative=None if c.get('positive_coverage_training') else torch.zeros_like(positive)
        for k,ident in enumerate(row['ids']):
            n=data[ident]['length'];positive[k,:n]=data[ident]['positive']
            if negative is not None:negative[k,:n]=data[ident]['negative']
        if tensor_hash(positive)!=row['positive_sha256'] or (negative is not None and tensor_hash(negative)!=row['negative_sha256']):raise ValueError('Changed actual label draw')
        fields=['loss','gradient_norm','positive_branch_loss','positive_flow_error']
        if negative is not None:fields+=['negative_branch_loss','negative_flow_error']
        elif any(k.startswith('negative_') for k in row):raise ValueError('Unexpected negative training branch')
        if any(not math.isfinite(row[k]) for k in fields) or row['gradient_norm']<=0 or row['loss']<0:raise ValueError('Invalid training loss/gradient')
    ckpath=run/f'ema_{count}.ckpt'
    if sha(ckpath)!=m['checkpoint_sha256']:raise ValueError('Changed saved checkpoint')
    ck=torch.load(ckpath,map_location='cpu',weights_only=False,mmap=True);parent=torch.load(c['checkpoint'],map_location='cpu',weights_only=False,mmap=True)
    original={k.replace('_orig_mod.',''):v for k,v in parent['ema'].items()}
    if set(ck['ema'])!=set(original) or any(not torch.equal(ck['ema'][k],v) for k,v in original.items()):raise ValueError('Saved generator changed')
    if state_hash(ck['ema'])!=m['generator_final'] or state_hash(ck['reference_fragment_adapter'])!=m['reference_final'] or state_hash(ck['raw_fragment_adapter'])!=m['adapter_final']:raise ValueError('Saved weight audit mismatch')
    if any(not torch.equal(ck['reference_fragment_adapter'][k],v) for k,v in parent['fragment_adapter'].items()) or ck['adapter_config']!=parent['adapter_config']:raise ValueError('Changed reference adapter or architecture')
    if state_hash(ck['fragment_adapter'])==m['adapter_initial'] or any(not torch.isfinite(v).all() for v in ck['fragment_adapter'].values()):raise ValueError('EMA update invalid')
    del ck,parent,original
    items=load_conditions(c['fragments'],c['control_ids'],'c20_center',cohort='train');records=[];wanted={(kind,step,ident) for ident in items for kind,step in [('initial',0),('pose',0),('null',count),('pose',count)]}
    if {(r['kind'],r['step'],r['target_id']) for r in m['controls']}!=wanted:raise ValueError('Missing numerical controls')
    for control in m['controls']:
        if not math.isfinite(control['latent_max_abs']) or control['latent_max_abs']>(1e-4 if control['kind']=='pose' else 1e-5):raise ValueError('Latent control failed')
        if control['kind']!='pose' and (control['max_ca_rmsd']>.2 or control['min_ca_lddt']<.99 or control.get('same_decisions',True) is not True):raise ValueError('Coordinate/control decision failed')
    with h5py.File(run/'evaluation_0.h5') as first,h5py.File(run/f'evaluation_{count}.h5') as last,h5py.File(c['initial_predictions']) as historical:
        for step,out in [(0,first),(count,last)]:
            if set(out)!={'conditioned','null'} or any(set(out[k])!=set(items) for k in out):raise ValueError('Wrong stored prediction inventory')
            rr=[]
            for ident,item in items.items():
                for mode in ('conditioned','null'):
                    g=out[mode+'/'+ident];z=g['latent'][:];bb=g['backbone'][:];n=item['length']
                    if z.shape!=(4,n,8) or bb.shape!=(4,n,4,3) or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Invalid stored prediction')
                    reference=historical['new/'+ident] if step==0 and mode=='conditioned' else first['null/'+ident] if mode=='null' else None
                    if reference is not None:
                        if np.max(abs(z-reference['latent'][:]))>1e-5:raise ValueError('Stored initialization/null changed')
                        for a,b in zip(bb,reference['backbone'][:]):
                            score=ca_metrics(a[:,1],b[:,1])
                            if score['ca_rmsd']>.2 or score['ca_lddt']<.99:raise ValueError('Stored coordinate parity failed')
                    if mode=='conditioned':
                        if g['pose_latent'].shape!=z.shape or np.max(abs(g['pose_latent'][:]-z))>1e-4:raise ValueError('Stored pose control failed')
                        rr.extend(raw_rows(bb,item['fragment'],item['start'],c['arm'],ident,item['family']))
            if rr!=next(r['records'] for r in m['evaluations'] if r['step']==step):raise ValueError('Stored sampling score mismatch')
            records.extend(dict(r,step=step) for r in rr)
    return dict(status='complete',arm=c['arm'],profile_only=c['profile_only'],profile_qualified=c['profile_only'],numerically_qualified=True,
                manifest_sha256=sha(path),checkpoint_sha256=m['checkpoint_sha256'],protocol_sha256=sha(c['protocol']),updates=count,controls=16,
                training_pairs=len(data),peak_reserved_GiB=m['peak_reserved_GiB'],training_seconds=m['training_seconds'],elapsed_seconds=m['elapsed_seconds'],
                records=records,scope='Numerical/frozen-weight training audit only. Raw motif retention does not establish designability or generalization.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0])
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Native-anchor training audit\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')


if __name__=='__main__':main()
