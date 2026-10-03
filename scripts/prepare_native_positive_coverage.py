"""Select fresh training references without looking at their assay outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from fragment_preference_calibration import native_inventory
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/native_positive_coverage_protocol.json';spec=json.loads(protocol.read_text())
    comparison=Path(spec['preceding_comparison']);prior=json.loads(comparison.read_text())
    if sha(comparison)!=spec['preceding_comparison_sha256'] or prior['status']!='complete' or any(prior['development_screen_qualified'].values()):raise ValueError('Changed preceding closed pilot')
    baseline=root/'runs/extra_fragment_validation_50188437/manifest.json';bc=json.loads(baseline.read_text())['config']
    excluded=set(native_inventory(bc));exclusions={i:['original64_reference_calibration'] for i in excluded};sources=[]
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in sources:sources.append(row)
        return str(path)
    bind(protocol);bind(comparison);bind(baseline)
    for source in bc['native_sources']:
        for key in ('manifest','report','refolded'):bind(source[key])
    registry=json.loads((root/'runs/jobs.json').read_text())
    for job in registry['jobs']:
        if job.get('completion_action')!='summarize_fragment_feedback':continue
        mp=root/f'runs/fragment_feedback_{job["id"]}/manifest.json'
        if not mp.exists():raise ValueError('Cannot establish exclusions for feedback job '+job['id'])
        c=json.loads(mp.read_text())['config'];bind(mp)
        for ident in c['selected_training_ids']:excluded.add(ident);exclusions.setdefault(ident,[]).append('feedback_'+job['id'])
    corpus=root/spec['corpus'];dm=json.loads((corpus/'manifest.json').read_text());dd=json.loads((corpus/'report.json').read_text());fr=corpus/'fragments.h5'
    if (dm['status']!='complete' or dd['status']!='complete' or not dd['training_gate_passed']
            or dd['manifest_sha256']!=sha(corpus/'manifest.json') or dd['fragments_sha256']!=sha(fr)
            or dm['training_protein_count']!=512):raise ValueError('Unqualified512training corpus')
    for path in [corpus/'manifest.json',corpus/'report.json',fr]:bind(path)
    rows=[];inventory_counts={}
    with h5py.File(fr) as f:
        if len(f['train'])!=512:raise ValueError('Changed training inventory')
        for bucket in (128,256,384,512):
            pool=[i for i in f['train'] if i not in excluded and (int(f['train/'+i].attrs['length'])+127)//128*128==bucket]
            pool.sort(key=lambda i:hashlib.sha256(f"{spec['selection_seed']}:{i}".encode()).hexdigest());inventory_counts[bucket]=len(pool)
            if len(pool)<spec['per_length_bucket'][str(bucket)]:raise ValueError('Insufficient disjoint training references')
            for k,ident in enumerate(pool[:spec['per_length_bucket'][str(bucket)]]):
                g=f['train/'+ident];q=g['conditions/'+spec['condition']];n=int(g.attrs['length'])
                if (ident in f['development'] or len(q.attrs['sequence'])!=20 or q['fragment'].shape!=(20,4,3)
                        or g['reference_z'].shape!=(n,8) or g['reference_backbone'].shape!=(n,4,3)
                        or not np.isfinite(g['reference_z'][:]).all()):raise ValueError('Invalid isolated/reference inputs')
                rows.append(dict(id=ident,family=str(g.attrs['family']),length=n,bucket=bucket,partition=k%4,start=int(q.attrs['start']),sequence=str(q.attrs['sequence'])))
    if len(rows)!=64 or set(r['id'] for r in rows)&excluded:raise ValueError('Changed disjoint64 selection')
    result=dict(status='selected',protocol=str(protocol),spec=spec,sources=sources,fragments=str(fr),selected=rows,
                target_ids=sorted(r['id'] for r in rows),excluded=exclusions,remaining_inventory_by_bucket=inventory_counts,
                scope='Training inputs only; no qualification, generation or designability claim. All64sources must enter the fixed two-decoder assay.')
    with a.output.open('x') as f:json.dump(result,f,indent=2)
    print('Bound64fresh training sources; exclusions',len(excluded),'remaining inventory',inventory_counts)


if __name__=='__main__':main()
