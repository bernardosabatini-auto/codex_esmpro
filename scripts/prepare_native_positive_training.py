"""Export every qualified positive and prepare the fixed profile/full recipe."""
import argparse
import json
from pathlib import Path
import h5py
from native_positive_training_core import qualified_inventory,load_positives,INPUT_KEYS
from prepare_overfit import sha


def prepare_labels(root,output):
    old_path=root/'runs/native_anchor_labels_20261003/manifest.json';new_path=root/'reports/native_positive_coverage_20261003.json'
    old=json.loads(old_path.read_text());new=json.loads(new_path.read_text());rows=qualified_inventory(old,new)
    control=root/'runs/native_anchor_training_50209404/manifest.json';oc=json.loads(control.read_text())['config']
    from native_anchor_training_core import load_pairs
    load_pairs(oc) # Independently recheck the original ten endpoints/qualification.
    d=dict(status='complete',rows=rows,sources=[],scope='All qualified original and new reference positives; no negative endpoints.')
    def bind(path):
        path=Path(path).resolve();d['sources'].append(dict(path=str(path),sha256=sha(path)));return str(path)
    for key,path in [('original_labels',old_path),('qualification',new_path),('matched_control',control),('coverage_protocol',root/'configs/native_positive_coverage_protocol.json')]:d[key]=bind(path)
    for s in new['source_reports']:bind(s['path'])
    for key in ('generation_manifest','generation_report'):bind(new[key])
    bind(oc['fragments'])
    output.mkdir(exist_ok=False);d['positives']=str((output/'positives.h5').resolve())
    with h5py.File(oc['fragments']) as fr,h5py.File(d['positives'],'x') as f:
        for row in rows:
            ident=row['target_id'];source=fr['train/'+ident];q=source['conditions/c20_center'];g=f.create_group(ident)
            g['positive']=source['reference_z'][:];g['fragment_latent']=q['latent'][:];g['fragment']=q['fragment'][:]
            g.attrs.update(sequence=q.attrs['sequence'],start=int(q.attrs['start']),length=row['length'])
    d['positives_sha256']=sha(d['positives']);(output/'manifest.json').write_text(json.dumps(d,indent=2)+'\n')
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',action='store_true');p.add_argument('--output',type=Path,required=True);p.add_argument('--profile-comparison',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];lp=root/'runs/native_positive_labels_20261003/manifest.json'
    labels=json.loads(lp.read_text()) if lp.exists() else prepare_labels(root,lp.parent)
    protocol=root/'configs/native_positive_training_protocol.json';spec=json.loads(protocol.read_text());oc=json.loads(Path(labels['matched_control']).read_text())['config']
    c=dict(positive_coverage_training=True,arm='positive_coverage',spec=spec,profile_only=a.profile,updates=spec['profile_updates'] if a.profile else spec['updates'],sources=[],
           training_ids=[r['target_id'] for r in labels['rows']],allocation_minutes=10,work_cap_seconds=480,**{k:oc[k] for k in INPUT_KEYS})
    def bind(path):
        path=Path(path).resolve();c['sources'].append(dict(path=str(path),sha256=sha(path)));return str(path)
    c['protocol']=bind(protocol);c['labels_manifest']=bind(lp)
    for key in ('checkpoint','decoder_checkpoint','fragments','initial_predictions'):bind(c[key])
    if not a.profile:
        if a.profile_comparison is None:raise ValueError('Full run needs qualified profile')
        c['profile_comparison']=bind(a.profile_comparison);profile=json.loads(a.profile_comparison.read_text())
        c['allocation_minutes']=profile['recommended_full_minutes'];c['work_cap_seconds']=60*c['allocation_minutes']-120
    load_positives(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print(c['arm'],c['updates'],len(c['training_ids']),c['allocation_minutes'])


if __name__=='__main__':main()
