"""Export only prospectively confirmed training pairs; retain all exclusions."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from compare_native_anchors import compare_native
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/native_anchor_training_protocol.json'
    spec=json.loads(protocol.read_text());comparison=root/'reports/native_anchor_comparison_20261003.json'
    d=json.loads(comparison.read_text())
    if d['status']!='complete' or not d['gate']['qualified']:raise ValueError('Native-anchor label gate failed; no export')
    runs=[Path(s['manifest']).parent for s in d['sources']]
    if json.loads(json.dumps(compare_native(runs,root)))!=d:raise ValueError('Qualification report does not reproduce')
    gm=root/'runs'/spec['label_generation']/'manifest.json';g=json.loads(gm.read_text());gc=g['config']
    if d['generation_manifest_sha256']!=sha(gm) or Path(gc['model_manifest']).parent.name!=spec['parent']:
        raise ValueError('Changed label generator')
    targets={r['id']:r for r in gc['selected']};pairs=[r for r in d['preferences'] if r['confirmed']]
    if len(pairs)!=d['gate']['confirmed'] or len(pairs)<8:raise ValueError('Changed confirmed label inventory')
    controls=[min(r['id'] for r in gc['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    a.output.mkdir(exist_ok=False);output=a.output/'pairs.h5';rows=[]
    with h5py.File(gc['fragments']) as fr,h5py.File(gm.parent/'predictions.h5') as pred,h5py.File(output,'x') as out:
        for pref in pairs:
            ident=pref['target_id'];row=targets[ident];source=fr['train/'+ident];q=source['conditions/c20_center']
            positive=source['reference_z'][:];negative=pred['new/'+ident+'/latent'][pref['negative_slot']]
            if not np.array_equal(pred['native/'+ident+'/latent'][:],np.broadcast_to(positive,(2,*positive.shape))):raise ValueError('Unqualified positive latent')
            if positive.shape!=(row['length'],8) or negative.shape!=positive.shape or not np.isfinite(positive).all() or not np.isfinite(negative).all():raise ValueError('Invalid latent labels')
            z=out.create_group(ident);z['positive']=positive;z['negative']=negative
            z['fragment_latent']=q['latent'][:];z['fragment']=q['fragment'][:]
            z.attrs.update(sequence=str(q.attrs['sequence']),start=int(q.attrs['start']),length=row['length'],family=row['family'])
            rows.append(dict(target_id=ident,length=row['length'],bucket=row['bucket'],negative_slot=pref['negative_slot'],
                             native_both_strict=pref['native_both_strict'],discovery_margin=pref['discovery_margin'],confirmation_margin=pref['confirmation_margin']))
    sources=[dict(path=str(path),sha256=sha(path)) for path in (protocol,comparison,gm,root/'reports'/(gm.parent.name+'.json'),gm.parent/'predictions.h5',Path(gc['fragments']),Path(gc['checkpoint']),Path(gc['decoder_checkpoint']))]
    m=dict(status='complete',spec=spec,protocol=str(protocol),comparison=str(comparison),sources=sources,
           generation_manifest=str(gm),checkpoint=gc['checkpoint'],decoder_checkpoint=gc['decoder_checkpoint'],fragments=gc['fragments'],
           pairs=str(output.resolve()),pairs_sha256=sha(output),rows=rows,control_ids=controls,
           excluded_training_ids=sorted(set(targets)-{r['target_id'] for r in rows}),
           scope='Only confirmed training-source pairs; all failed source outcomes remain in qualification reports. No evaluation labels or generation-noise coupling used.')
    (a.output/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print('Exported',len(rows),'qualified pairs; excluded',len(m['excluded_training_ids']),'sources; buckets',sorted({r['bucket'] for r in rows}))


if __name__=='__main__':main()
