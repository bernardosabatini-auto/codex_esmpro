"""Audit frame-probe labels and reconstructions before any training proposal."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_fragment_feedback import selected_ids
from prepare_overfit import sha
from summarize_fragment_training import interval


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),target_frame_training_qualified=False)
    c=m['config']
    for key in ('protocol','parent_manifest','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed source')
    if c['conditions']!=['f30_left','f30_center','f30_right']:raise ValueError('Changed conditions')
    index={(r['target_id'],r['condition']):r for r in m['records']};expected={(i,k) for i in c['training_ids'] for k in c['conditions']}
    if len(m['records'])!=24 or set(index)!=expected:raise ValueError('Incomplete probe')
    for key,tolerance in [('encoding_controls',.05),('pose_controls',1e-4)]:
        rows=m[key]
        if len(rows)!=8 or {r['target_id'] for r in rows}!=set(c['training_ids']) or any(not np.isfinite(r['latent_rmse']) or r['latent_rmse']>tolerance or r.get('coordinate_max_abs',0)>1e-4 for r in rows):raise ValueError('Invalid probe controls')
    with h5py.File(c['fragments']) as src,h5py.File(run/'predictions.h5') as f:
        if c['training_ids']!=selected_ids(src) or set(f)!=set(c['training_ids']):raise ValueError('Changed training-only panel')
        for ident in c['training_ids']:
            g=src['train/'+ident];raw=g['reference_backbone'][:];original=g['reference_z'][:]
            if set(f[ident])!=set(c['conditions']):raise ValueError('Wrong condition inventory')
            for condition in c['conditions']:
                saved=f[ident+'/'+condition];row=index[ident,condition];q=g['conditions/'+condition];latent=q['latent'][:];st=int(q.attrs['start']);k=len(latent);z=saved['latent'][:]
                if z.shape!=original.shape or not np.isfinite(z).all() or set(saved)!={'latent','original','anchored'}:raise ValueError('Invalid encoded target')
                metrics=dict(latent_before_rmse=float(np.sqrt(np.mean((original[st:st+k]-latent)**2))),latent_after_rmse=float(np.sqrt(np.mean((z[st:st+k]-latent)**2))),full_target_latent_change_rmse=float(np.sqrt(np.mean((z-original)**2))))
                if any(abs(row[key]-value)>1e-6 for key,value in metrics.items()):raise ValueError('Latent score mismatch')
                for mode in ['original','anchored']:
                    bb=saved[mode][:]
                    if bb.shape!=raw.shape or not np.isfinite(bb).all():raise ValueError('Invalid reconstruction')
                    actual=dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**ca_metrics(bb[:,1],raw[:,1]))
                    if any(abs(row[mode][key]-value)>1e-6 for key,value in actual.items()):raise ValueError('Reconstruction score mismatch')
    rows=m['records'];before=float(np.mean([r['latent_before_rmse'] for r in rows]));after=float(np.mean([r['latent_after_rmse'] for r in rows]));delta=interval([np.mean([r['latent_before_rmse']-r['latent_after_rmse'] for r in rows if r['target_id']==i]) for i in c['training_ids']]);qualified_counts={mode:sum(r[mode]['coarse_valid'] and r[mode]['ca_rmsd']<=.5 for r in rows) for mode in ['original','anchored']};reduction=(before-after)/max(before,1e-12)
    qualified=reduction>=.2 and delta['ci95'][0]>0 and min(qualified_counts.values())>=23
    return dict(status='complete',manifest_sha256=sha(path),predictions_sha256=sha(run/'predictions.h5'),conditions=24,training_families=8,latent_before_rmse=before,latent_after_rmse=after,relative_latent_gap_reduction=reduction,before_minus_after_family_interval=delta,mean_full_target_latent_change_rmse=float(np.mean([r['full_target_latent_change_rmse'] for r in rows])),valid_reconstruction_under_half_A=qualified_counts,target_frame_training_qualified=bool(qualified),interpretation='Training-only representation diagnostic. Targets already use whole-protein PCA; anchoring changes that convention. This is not generation, generalization or designability evidence.',records=rows,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fragment-anchored target-frame probe\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
