"""Bounded CPU profile/full closure, preserving every attempted backbone."""
import argparse
import json
from pathlib import Path
import time
import h5py
import numpy as np
import torch
from latentfold.local_closure import close_backbone,topology,geometry_audit
from extra_fragment_validation_core import load_conditions
from local_closure_core import make_config,ROTATION,OFFSET
from profile_gpu import atomic_json
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',action='store_true');p.add_argument('--profile-report',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    torch.set_num_threads(1);c=make_config(root,a.profile,a.profile_report);spec=c['spec']
    if torch.cuda.is_initialized():raise ValueError('CPU-only closure must not initialize CUDA')
    ids=[r['id'] for r in c['selected']];items=load_conditions(c['fragments'],ids,'c20_center',cohort='train')
    a.output.mkdir(exist_ok=False);tick=time.monotonic();deadline=tick+spec['execution']['profile_work_cap_seconds' if a.profile else 'full_work_cap_seconds']
    m=dict(status='running',config=c,records=[],controls=[],gpus_used=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        with h5py.File(c['source_predictions']) as inputs,h5py.File(a.output/'predictions.h5','x') as out:
            for ident in c['profile_ids']:
                item=items[ident];parent=inputs['parent/'+ident+'/backbone'][0]
                for kind in ('noop','perturbation'):
                    source=parent.copy()
                    if kind=='perturbation':
                        residues=topology(len(parent),item['start'],20,4)['residues']
                        source[residues]+=.05*np.random.default_rng(2026100461).normal(size=(len(residues),4,3))
                    bb,r=close_backbone(source,parent,item['start'],20,spec,deadline=deadline)
                    g=out.create_group('controls/'+kind+'/'+ident);g['source']=source;g['backbone']=bb
                    geometry=geometry_audit(bb,parent,item['start'],20)
                    if (kind=='noop' and not np.array_equal(bb,parent)) or not geometry['valid']:
                        raise ValueError('Local closure positive/no-op control failed')
                    m['controls'].append(dict(kind=kind,target_id=ident,**r))
            for row in c['selected']:
                ident=row['id'];item=items[ident]
                for arm in spec['execution']['arms']:
                    reference='native_direct' if arm=='native_cond' else 'parent'
                    results=[]
                    for slot in range(4):
                        source=inputs[arm+'/'+ident+'/backbone'][slot];parent=inputs[reference+'/'+ident+'/backbone'][slot]
                        bb,r=close_backbone(source,parent,item['start'],20,spec,deadline=deadline)
                        results.append(bb);m['records'].append(dict(arm=arm,target_id=ident,slot=slot,reference=reference,**r))
                        if ident in c['profile_ids'] and slot==0:
                            posed,rr=close_backbone(source.astype(np.float64)@ROTATION+OFFSET,parent.astype(np.float64)@ROTATION+OFFSET,item['start'],20,spec,deadline=deadline)
                            out.create_dataset('pose/'+arm+'/'+ident,data=posed)
                            error=float(np.max(np.abs(posed-(bb.astype(np.float64)@ROTATION+OFFSET))))
                            m['controls'].append(dict(kind='pose',arm=arm,target_id=ident,max_abs=error,**rr))
                            if error>.005:raise ValueError('Closure proper-pose equivariance failed')
                    out.create_dataset(arm+'/'+ident+'/backbone',data=np.stack(results));out.flush()
                    atomic_json(a.output/'manifest.json',m)
                print('closed',ident,flush=True)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
