"""Audit teacher-label shard completeness, reconstruction and coarse clustering."""
import argparse,json
from collections import Counter
from pathlib import Path
import h5py,numpy as np
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='No manifest');d=dict(status=m['status'],scope=m.get('scope'))
    if m['status']=='complete':
        rows=m['records']
        if len(rows)!=128 or len({r['id'] for r in rows})!=128 or len(m['batches'])!=128:raise ValueError('incomplete shard')
        with h5py.File(run/'labels.h5') as h:
            if set(h)!={r['id'] for r in rows}:raise ValueError('label targets differ')
            for row in rows:
                g=h[row['id']];n=row['length']
                if g['teacher_z'].shape!=(16,n,8) or g['reference_z'].shape!=(n,8) or g['teacher_backbone'].shape!=(16,n,4,3):raise ValueError('invalid labels')
                if not np.isfinite(g['teacher_z'][:]).all() or not np.isfinite(g['reference_z'][:]).all():raise ValueError('nonfinite latent labels')
        d.update(targets=128,teacher_samples=2048,valid_teacher_samples=sum(r['valid_samples'] for r in rows),cluster_histogram=dict(Counter(r['teacher_clusters'] for r in rows)),native_reconstruction_rmsd_mean=float(np.mean([r['native_reconstruction']['ca_rmsd'] for r in rows])),teacher_reconstruction_rmsd_mean=float(np.mean([r['teacher_reconstruction']['ca_rmsd'] for r in rows])),native_cached_latent_rmse_mean=float(np.mean([r['native_cached_latent_rmse'] for r in rows])),max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3)
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete shard')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Teacher label generation','',f"Status: {d['status']}.",'',str(d['scope'])]
    if d['status']=='complete':lines+=['',f"Targets: 128. Teacher samples: 2048; coarse-valid: {d['valid_teacher_samples']}. Mean reconstruction RMSD: reference {d['native_reconstruction_rmsd_mean']:.4f} A, teacher sample zero {d['teacher_reconstruction_rmsd_mean']:.4f} A.",'',f"Teacher cluster-count histogram: {d['cluster_histogram']}.",'','Clusters are geometry-based training strata, not experimentally established states or populations. Fresh reference and teacher latents use the same encoder path.']
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
