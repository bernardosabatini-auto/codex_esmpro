"""Independently score every frozen integration output and oracle-path probe."""
import argparse,json,math
from pathlib import Path
import h5py
import numpy as np
import torch
from fragment_decoder_integrator_core import audit
from extra_fragment_validation_core import load_conditions
from fragment_validation_core import raw_rows
from latentfold.flow import target_noise
from latentfold.ensemble_metrics import backbone_geometry
from compare_extra_fragment_refolds import clustered
from prepare_overfit import sha


def describe(bb,item,arm,ident,bucket):
    rows=raw_rows(bb,item['fragment'],item['start'],arm,ident,item['family']);g=backbone_geometry(bb)
    for k,r in enumerate(rows):r.update(bucket=bucket,peptide_failure=bool(g['peptide_outlier_fraction'][k]>.05),clash_failure=bool(g['ca_clashing_residue_fraction'][k]>.01),gap_failure=bool(g['ca_gap_fraction'][k]>.01))
    return rows


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text()) if mp.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];spec,gc,source=audit(c);ids=[r['id'] for r in c['selected']]
    if (m['training_updates_executed']!=0 or len(m['controls'])!=100 or len(m['timing'])!=128
            or m['model_initial']!=source['evaluated_model_sha256'] or m['model_final']!=m['model_initial']
            or m['original_initial']!=source['frozen_original'] or m['original_final']!=m['original_initial']
            or not math.isfinite(m['peak_reserved_GiB']) or m['peak_reserved_GiB']>75
            or m['predictions_sha256']!=sha(run/'predictions.h5')):raise ValueError('Incomplete frozen diagnostic or changed weights')
    pose_ids={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
    wanted={(kind,i) for i in ids for kind in ('original_native','three_cond','three_null')}|{('pose_ten_cond',i) for i in pose_ids}
    controls={(r['kind'],r['target_id']):r for r in m['controls']}
    if set(controls)!=wanted or {(r['target_id'],r['arm'],r['steps']) for r in m['timing']}!={(i,a,s) for i in ids for a in ('cond','null') for s in (3,10)}:raise ValueError('Changed control/timing inventory')
    if any(not math.isfinite(r['seconds']) or r['seconds']<=0 for r in m['timing']):raise ValueError('Invalid timing')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');free=[];path=[];original=[]
    def check(bb,n):
        if bb.shape!=(4,n,4,3) or not np.isfinite(bb).all():raise ValueError('Invalid backbone shape or values')
    def control(kind,i,x,y,tolerance):
        error=float(np.max(abs(x-y)))
        if not math.isfinite(error) or error>tolerance or error!=controls[kind,i]['max_abs']:raise ValueError('Changed numeric control: '+kind)
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['source_predictions']) as old,h5py.File(c['fragments']) as fr:
        if set(f)!={'inputs','original_native','free','path'} or set(f['inputs'])!=set(ids) or set(f['original_native'])!=set(ids) or set(f['free'])!={'cond','null'} or set(f['path'])!={'cond','null','original_unmasked'}:raise ValueError('Changed diagnostic inventory')
        for arm in ('cond','null'):
            if set(f['free/'+arm])!={'3','10'} or any(set(f[f'free/{arm}/{s}'])!=set(ids) for s in (3,10)):raise ValueError('Missing free predictions')
        for arm in ('cond','null','original_unmasked'):
            if set(f['path/'+arm])!={'0','1','2','3'} or any(set(f[f'path/{arm}/{t}'])!=set(ids) for t in range(4)):raise ValueError('Missing path predictions')
        for row in c['selected']:
            ident=row['id'];n=row['length'];item=items[ident];keep=item['keep'].numpy();noise=f['inputs/'+ident+'/noise'][:]
            expected=torch.cat([target_noise([ident],[4*n],3,seed=spec['seed'],sample_index=k,stream=spec['decoder_stream']) for k in range(4)]).numpy()
            z=np.repeat(fr['train/'+ident+'/reference_z'][:][None],4,axis=0);z[:,keep]=0
            if not np.array_equal(noise,expected) or not np.array_equal(z,f['inputs/'+ident+'/masked_latent'][:]):raise ValueError('Changed input noise or motif masking')
            bb=f['original_native/'+ident+'/backbone'][:];check(bb,n);control('original_native',ident,bb,old['native_direct/'+ident+'/backbone'][:],1e-5)
            original.extend(describe(bb,item,'original_native',ident,row['bucket']))
            for arm in ('cond','null'):
                for steps in (3,10):
                    g=f[f'free/{arm}/{steps}/{ident}'];bb=g['backbone'][:];check(bb,n)
                    if steps==3:control('three_'+arm,ident,bb,old['native_'+arm+'/'+ident+'/backbone'][:],1e-5)
                    if steps==10 and arm=='cond' and ident in pose_ids:control('pose_ten_cond',ident,bb,g['pose_backbone'][:],1e-4)
                    free.extend([dict(r,steps=steps) for r in describe(bb,item,arm,ident,row['bucket'])])
            clean=fr['train/'+ident+'/reference_backbone'][:].reshape(1,4*n,3)/10;clean=clean-clean.mean(1,keepdims=True)
            initial=noise-noise.mean(1,keepdims=True)
            for index,value in enumerate(spec['probe_times']):
                t=np.float32(value);noisy=(1-t)*initial+t*clean
                for arm in ('cond','null','original_unmasked'):
                    g=f[f'path/{arm}/{index}/{ident}'];bb=g['backbone'][:];v=g['velocity'][:];check(bb,n)
                    if float(g.attrs['t'])!=float(t) or v.shape!=(4,4*n,3) or not np.isfinite(v).all():raise ValueError('Changed probe time or invalid velocity')
                    reconstructed=(noisy+(1-t)*v).reshape(4,n,4,3)*10
                    if float(np.max(abs(bb-reconstructed)))>2e-4:raise ValueError('Saved probe does not match its interpolation and velocity')
                    mse=((bb.reshape(4,4*n,3)/10-clean)**2).reshape(4,n,4,3).mean((2,3))
                    rr=describe(bb,item,arm,ident,row['bucket'])
                    for k,r in enumerate(rr):
                        motif=float(mse[k,keep].mean());scaffold=float(mse[k,~keep].mean());weight=float(1/((1-t)**2+1e-5))
                        path.append(dict(r,time_index=index,t=float(t),motif_coordinate_mse_nm2=motif,scaffold_coordinate_mse_nm2=scaffold,motif_fm=motif*weight,scaffold_fm=scaffold*weight))
    if len(free)!=512 or len(path)!=1536 or len(original)!=128:raise ValueError('Changed output denominators')
    def summary(rr,**keys):
        return dict(keys,samples=len(rr),raw=sum(r['raw_gate_passed'] for r in rr),valid=sum(r['coarse_valid'] for r in rr),
            motif_fit_without_geometry=sum(r['motif_ca_rmsd']<=1 and r['motif_drms']<=1 for r in rr),mean_motif_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr])),
            **{k:sum(r[k] for r in rr) for k in ('peptide_failure','clash_failure','gap_failure')})
    free_summary=[summary([r for r in free if r['arm']==a and r['steps']==s],arm=a,steps=s) for a in ('cond','null') for s in (3,10)]
    path_summary=[]
    for a in ('cond','null','original_unmasked'):
        for index,value in enumerate(spec['probe_times']):
            rr=[r for r in path if r['arm']==a and r['time_index']==index]
            path_summary.append(dict(summary(rr,arm=a,t=value),**{k:float(np.mean([r[k] for r in rr])) for k in ('motif_coordinate_mse_nm2','scaffold_coordinate_mse_nm2','motif_fm','scaffold_fm')}))
    contrasts=[];families=sorted({r['family'] for r in free})
    for a,s,b,u in [('cond',10,'cond',3),('null',10,'null',3),('cond',10,'null',10),('cond',3,'null',3)]:
        metrics={k:clustered([np.mean([float(r[k]) for r in free if r['family']==fam and r['arm']==a and r['steps']==s])-np.mean([float(r[k]) for r in free if r['family']==fam and r['arm']==b and r['steps']==u]) for fam in families]) for k in ('raw_gate_passed','coarse_valid','motif_ca_rmsd')}
        contrasts.append(dict(candidate=f'{a}_{s}',reference=f'{b}_{u}',metrics=metrics))
    timing=[dict(arm=a,steps=s,seconds=sum(r['seconds'] for r in m['timing'] if r['arm']==a and r['steps']==s)) for a in ('cond','null') for s in (3,10)]
    return dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],source_manifest_sha256=sha(c['source_manifest']),protocol_sha256=sha(c['protocol']),
        controls=100,free_summary=free_summary,path_summary=path_summary,original_summary=summary(original,arm='original_native'),contrasts=contrasts,timing=timing,
        peak_reserved_GiB=m['peak_reserved_GiB'],elapsed_seconds=m['elapsed_seconds'],free_records=free,path_records=path,
        scope='Frozen-model diagnostic on repeated32training proteins. All contexts are native oracles; t>0 path probes additionally contain native coordinates. '
              'Free sampling and oracle denoising are reported separately. No training, designability, refolding or generalization claim. Original3step failure is retained;10steps does not retrospectively qualify that recipe.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1)
    d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    visible={k:v for k,v in d.items() if k not in ('free_records','path_records')}
    a.output.with_suffix('.md').write_text('# Frozen decoder integration diagnostic\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))


if __name__=='__main__':main()
