"""Prospective training-source designability calibration, balanced by length."""
import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from prepare_overfit import sha


def select_sources(spec, rows, original_ids):
    selected = []
    for cohort in spec['cohorts']:
        for bucket in spec['buckets']:
            pool = [r for r in rows if r['bucket'] == bucket and
                    (r['id'] in original_ids) == (cohort == 'original512')]
            pool.sort(key=lambda r: hashlib.sha256(f"{spec['seed']}:{cohort}:{r['id']}".encode()).hexdigest())
            if len(pool) < spec['per_cohort_per_bucket']:
                raise ValueError('Insufficient source stratum')
            selected.extend(dict(r, cohort=cohort, partition=k % 4)
                            for k, r in enumerate(pool[:spec['per_cohort_per_bucket']]))
    if len({r['id'] for r in selected}) != len(selected):
        raise ValueError('Duplicate source')
    return selected


def audit_inputs(c):
    for key in ('generation_manifest', 'predictions', 'protocol', 'fragments', 'confidence_report'):
        if sha(c[key]) != c[key+'_sha256']:
            raise ValueError('Changed source calibration input: '+key)
    index = json.loads(Path(c['generation_manifest']).read_text())
    spec = json.loads(Path(c['protocol']).read_text())
    if index['status'] != 'complete' or index['spec'] != spec:
        raise ValueError('Changed source calibration protocol')
    for path, digest in index['sources'].items():
        if sha(path) != digest:
            raise ValueError('Changed source selection provenance')
    bm = json.loads(Path(index['corpus_manifest']).read_text())
    om = json.loads(Path(index['original_manifest']).read_text())
    selected = select_sources(spec, bm['config']['training_targets'],
                              {r['id'] for r in om['config']['training_targets']})
    if index['selected'] != selected or len(selected) != 128:
        raise ValueError('Changed fixed128-source panel')
    rows = [r for r in selected if r['partition'] == c['partition']]
    if c['partition'] not in range(4) or c['expected_backbones'] != 32 or len(c['entries']) != 32:
        raise ValueError('Changed source partition')
    if any(c[k] != spec[k] for k in ('num_sequences','temperature','mpnn_seed','precision','seed')):
        raise ValueError('Changed source assay recipe')
    if c.get('mpnn_mode','ca') != spec['mpnn_mode'] or c['fragments_sha256'] != bm['fragments_sha256']:
        raise ValueError('Changed MPNN mode or source corpus')
    confidence = {r['id']:r for r in json.loads(Path(c['confidence_report']).read_text())['records']}
    with h5py.File(c['predictions']) as raw, h5py.File(c['fragments']) as data:
        if set(raw) != {'motifs'} | {r['dataset'] for r in c['entries']}:
            raise ValueError('Changed source inventory')
        for k, (row, entry) in enumerate(zip(rows, c['entries'])):
            ident = row['id']; group = data['train/'+ident]; q = group['conditions/'+spec['condition']]
            wanted = make_entry(row, q, k, confidence[ident])
            if entry != wanted:
                raise ValueError('Changed supplied source constraint')
            if not np.array_equal(raw[entry['dataset']][0], group['reference_backbone'][:]) or not np.array_equal(raw['motifs/'+ident][:], q['fragment'][:]):
                raise ValueError('Changed training-source coordinates')


def make_entry(row, q, k, confidence):
    name = f"source_{row['partition']}_{k:03d}"
    return dict(name=name, dataset=name, head=row['cohort'], arm=row['cohort'], target_id=row['id'],
                family=row['family'], length=row['length'], bucket=row['bucket'], slot=0,
                generation_slot=0, fixed_start=int(q.attrs['start']), motif_start=int(q.attrs['start']),
                fixed_sequence=str(q.attrs['sequence']), repeatability_control=k in (0, 16),
                afdb_mean_plddt=confidence['afdb_mean_plddt'])


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output-prefix',type=Path,required=True)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    protocol = root/'configs/fragment_source_designability_protocol.json'
    spec = json.loads(protocol.read_text()); corpus = root/spec['corpus']
    original = root/spec['original_manifest']; bm = corpus/'manifest.json'
    original_ids = {r['id'] for r in json.loads(original.read_text())['config']['training_targets']}
    selected = select_sources(spec,json.loads(bm.read_text())['config']['training_targets'],original_ids)
    confidence_path = root/spec['confidence_report']
    confidence = {r['id']:r for r in json.loads(confidence_path.read_text())['records']}
    indexpath = Path(str(args.output_prefix)+'_inventory.json').resolve()
    index = dict(status='complete',spec=spec,selected=selected,corpus_manifest=str(bm),
                 original_manifest=str(original),sources={str(p):sha(p) for p in (bm,original,protocol,confidence_path)})
    with indexpath.open('x') as f: json.dump(index,f,indent=2)
    prior = json.loads((root/'runs/fragment_strict_followup_50112017/manifest.json').read_text())['config']
    with h5py.File(corpus/'fragments.h5') as data:
        for partition in range(4):
            configpath = Path(str(args.output_prefix)+f'_{partition}.json').resolve()
            inputs = configpath.with_suffix('.h5')
            c = {k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')}
            c.update(assay='fragment_source_refold',partition=partition,entries=[],expected_backbones=32,
                     seed=spec['seed'],allocation_minutes=45,work_cap_seconds=2610)
            for key,path in [('generation_manifest',indexpath),('protocol',protocol),('fragments',corpus/'fragments.h5'),('confidence_report',confidence_path)]:
                c[key]=str(path);c[key+'_sha256']=sha(path)
            with h5py.File(inputs,'x') as out:
                for k,row in enumerate(r for r in selected if r['partition']==partition):
                    g = data['train/'+row['id']]; q = g['conditions/'+spec['condition']]
                    entry = make_entry(row,q,k,confidence[row['id']]); c['entries'].append(entry)
                    out.create_dataset(entry['dataset'],data=g['reference_backbone'][:][None])
                    out.create_dataset('motifs/'+row['id'],data=q['fragment'][:])
            c.update(predictions=str(inputs),predictions_sha256=sha(inputs))
            audit_inputs(c)
            with configpath.open('x') as f: json.dump(c,f,indent=2)
            print(partition,len(c['entries']),flush=True)


if __name__ == '__main__':
    main()
