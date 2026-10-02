"""Audit precision/pose diagnostics without changing a failed training gate."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'))
    c=m['config']
    for key in ('parent_manifest','checkpoint','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if sha(run/'predictions.h5')!=m['predictions_sha256']:raise ValueError('Diagnostic outputs changed')
    parent=json.loads(Path(c['parent_manifest']).read_text());variants=('fp32_rounded_pose','fp64_original','fp64_exact_pose','fp64_arbitrary_pose','fp64_rounded_pose');wanted={(i,v) for i in c['control_ids'] for v in variants}
    if len(m['records'])!=20 or {(r['target_id'],r['variant']) for r in m['records']}!=wanted:raise ValueError('Incomplete diagnostic')
    with h5py.File(run/'predictions.h5') as f:
        for r in m['records']:
            g=f[r['target_id']+'/'+r['variant']];ref=f[r['target_id']+'/'+r['baseline']];bb=g['backbone'][:];before=ref['backbone'][:];z=g['latent'][:];bz=ref['latent'][:];scores=[ca_metrics(bb[i,:,1],before[i,:,1]) for i in range(4)];actual=dict(latent_max_abs=float(np.max(abs(z-bz))),max_ca_rmsd=max(x['ca_rmsd'] for x in scores),min_ca_lddt=min(x['ca_lddt'] for x in scores),same_validity=bool(np.array_equal(backbone_geometry(bb)['coarse_valid'],backbone_geometry(before)['coarse_valid'])))
            if any(abs(r[k]-v)>1e-7 for k,v in actual.items()):raise ValueError('Saved diagnostic score mismatch')
    old={r['target_id']:r['pose_latent_max_abs'] for r in parent['geometry_controls'] if r['step']==500};reproduced=all(abs(r['latent_max_abs']-old[r['target_id']])<=1e-5 for r in m['records'] if r['variant']=='fp32_rounded_pose');exact=all(r['latent_max_abs']<=1e-4 and r['max_ca_rmsd']<=.01 and r['min_ca_lddt']>=.999 and r['same_validity'] for r in m['records'] if r['variant'] in ('fp64_exact_pose','fp64_arbitrary_pose'));rounding=all(r['max_ca_rmsd']<=.01 and r['min_ca_lddt']>=.999 and r['same_validity'] for r in m['records'] if r['variant'] in ('fp64_original','fp64_rounded_pose','fp32_rounded_pose'))
    return dict(status='complete',original_failure_reproduced=reproduced,exact_rigid_pose_passed=exact,small_coordinate_rounding_structurally_stable=rounding,corrected_precision_profile_qualified=reproduced and exact and rounding,records=m['records'],elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],manifest_sha256=sha(path),predictions_sha256=m['predictions_sha256'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fragment-distance pose precision diagnostic\n\nFrozen failed500update checkpoint,4predeclared control proteins,4noises,6precision/pose variants. No training or model-quality rescue. Original failed control remains failed. Exact double-precision rigid transforms are distinguished from FP32 coordinate-rounding perturbations; saved backbones and every contrast audited.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
