"""Read-only latent error versus teacher spread before capacity training."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=json.loads(a.selection.read_text());targets={r['id']:r for r in s['targets']};source=Path('runs/reflow_49662855/manifest.json');manifest=json.loads(source.read_text());rows=[];sources={}
    for shard in manifest['config']['pair_shards']:
        path=Path(shard['manifest']);pairs=path.parent/'pairs.h5'
        if sha(path)!=shard['manifest_sha256'] or sha(pairs)!=shard['pairs_sha256']:raise ValueError('pair provenance changed')
        sources[str(pairs)]=shard['pairs_sha256']
        with h5py.File(pairs) as h:
            for ident in sorted(set(h)&set(targets)):
                r=targets[ident]
                if h[ident].attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('sequence mismatch')
                x=h[ident]['endpoint'][:]
                with h5py.File(r['source_labels']) as labels:
                    g=labels[ident];y=g['teacher_z'][:][g['coarse_valid'][:].astype(bool)];ref=g['reference_z'][:]
                if x.shape!=(16,r['length'],8):raise ValueError('endpoint shape mismatch')
                nearest=np.sqrt(((x[:,None]-y[None])**2).mean((2,3))).min(1)
                rows.append(dict(
                    id=ident,
                    nearest_teacher_latent_rmse=float(nearest.mean()),
                    teacher_latent_spread=float(np.sqrt(((y-y.mean(0))**2).mean())),
                    student_latent_spread=float(np.sqrt(((x-x.mean(0))**2).mean())),
                    student_reference_rmse=float(np.sqrt(((x-ref)**2).mean())),
                    teacher_reference_rmse=float(np.sqrt(((y-ref)**2).mean())),
                ))
    if len(rows)!=32:raise ValueError('incomplete frozen panel')
    summary={k:float(np.mean([r[k] for r in rows])) for k in rows[0] if k!='id'};result=dict(status='complete',selection=str(a.selection),selection_sha256=sha(a.selection),sources=sources,summary=summary,rows=rows)
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');lines=['# Initial student latent error versus reliable teacher spread','','Frozen reliable32 panel, old initialization25-step CFG2 samples from existing reflow-generation runs. No new GPU inference. Teacher latents use one cached-reference frame per sequence. These are latent-space diagnostics, not structural-state coverage, and do not select or change the panel.','']
    lines += [f'- {k}: {v:.6f}' for k,v in summary.items()];a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(summary)

if __name__=='__main__':main()
