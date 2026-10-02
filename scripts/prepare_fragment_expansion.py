"""Select existing reference-only training data and preserve original fragments."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_conditioning import AMINO_ACIDS
from prepare_overfit import sha


EXTRA_KEYS=('expanded_protocol','base_manifest','base_fragments','pool_inventory')


def audit_sources(c):
    for key in EXTRA_KEYS+('training_manifest','training_labels'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed expanded data source '+key)
    meta=json.loads(Path(c['training_manifest']).read_text());base=json.loads(Path(c['base_manifest']).read_text());oldids={r['id'] for r in base['config']['training_targets']};rows=c['training_targets'];dev=c['development_rows'];protocol=json.loads(Path(c['expanded_protocol']).read_text());count=protocol.get('training_proteins',128);quotas={int(k):v for k,v in protocol.get('bucket_counts',{'128':24,'256':40,'384':32,'512':32}).items()}
    if count not in (128,512) or c.get('training_protein_count',128)!=count:raise ValueError('Undeclared expansion size')
    if meta['status']!='complete' or rows!=meta['targets'] or len(rows)!=count or len({r['id'] for r in rows})!=count or len({r['family'] for r in rows})!=count or c['base_training_ids']!=sorted(oldids):raise ValueError('Invalid expanded inventory')
    if {r['family'] for r in rows}&{r['family'] for r in dev} or {r['sequence_sha256'] for r in rows}&{hashlib.sha256(r['sequence'].encode()).hexdigest() for r in dev}:raise ValueError('Development overlap')
    counts={b:sum(r['bucket']==b for r in rows) for b in (128,256,384,512)}
    if counts!=quotas:raise ValueError('Wrong expansion quotas')
    for src in meta['source_shards']:
        if sha(src['manifest'])!=src['manifest_sha256'] or sha(src['labels'])!=src['labels_sha256']:raise ValueError('Changed source shard')
    handles={}
    try:
        with h5py.File(c['training_labels']) as combined,h5py.File(c['base_fragments']) as old:
            if set(combined)!={r['id'] for r in rows}:raise ValueError('Combined reference inventory changed')
            for r in rows:
                ident=r['id'];g=combined[ident]
                if hashlib.sha256(r['sequence'].encode()).hexdigest()!=r['sequence_sha256'] or set(r['sequence'])-set(AMINO_ACIDS):raise ValueError('Invalid sequence')
                if ident in oldids:source=old['train/'+ident]
                else:
                    lp=r['source_labels']
                    if lp not in handles:handles[lp]=h5py.File(lp)
                    source=handles[lp][ident]
                    if source.attrs['sequence_sha256']!=r['sequence_sha256'] or r['mean_teacher_confidence']<.8 or r['reference_ca_error']>.02 or r['reference_encoding_parity_rmse']>.05:raise ValueError('New reference audit failed')
                for key in ('reference_backbone','reference_z'):
                    if not np.array_equal(g[key][:],source[key][:]):raise ValueError('Combined native arrays changed')
                if len(g['reference_z'])!=r['length'] or not bool(backbone_geometry(g['reference_backbone'][:][None])['coarse_valid'][0]):raise ValueError('Invalid native geometry')
    finally:
        for f in handles.values():f.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--size',type=int,choices=[128,512],default=128);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol_path=root/('configs/fragment_expansion512_protocol.json' if a.size==512 else 'configs/fragment_expansion_protocol.json');basepath=root/('runs/fragment_data_49945596/manifest.json' if a.size==512 else 'runs/fragment_data_49885689/manifest.json');base=json.loads(basepath.read_text());invpath=root/'runs/expanded_labels_inventory.json';inv=json.loads(invpath.read_text());parent=json.loads((root/'reports/fragment_training_49929751.json').read_text());strict=json.loads((root/'reports/fragment_strict_capacity_49929751.json').read_text())
    if not base['training_gate_passed'] or not inv['reconstruction_gate_passed'] or parent['status']!='complete' or not parent['capacity_gate_passed'] or not any(r['run']=='fragment_training_49929751' and r['cohort']=='train' and r['arms']['conditioned']['strict_raw']>=8 for r in strict['summaries']):raise ValueError('Expansion prerequisite failed')
    if a.size==512:
        broad=json.loads((root/'reports/fragment_data_breadth_comparison_49951202.json').read_text());assay=json.loads((root/'reports/trained_fragment_designability_49961674.json').read_text())
        if broad['status']!='complete' or assay['status']!='complete' or not any(r['step']==2000 and r['cohort']=='development' and r['metric']=='motif_drms' and r['candidate_minus_baseline']['ci95'][1]<0 for r in broad['comparisons']):raise ValueError('512breadth prerequisite failed')
    c=base['config'].copy();rows=list(c['training_targets']);oldids={r['id'] for r in rows};families={r['family'] for r in rows}|{r['family'] for r in c['development_rows']};seqs={hashlib.sha256(r['sequence'].encode()).hexdigest() for r in rows+c['development_rows']};candidates={};sources=[]
    for shard in inv['source_shards']:
        mp=Path(shard['manifest']);m=json.loads(mp.read_text());lp=mp.parent/'labels.h5'
        if m['status']!='complete' or sha(mp)!=shard['manifest_sha256'] or sha(lp)!=shard['labels_sha256']:raise ValueError('Unverified existing shard')
        sources.append(dict(manifest=str(mp),manifest_sha256=sha(mp),labels=str(lp),labels_sha256=shard['labels_sha256']));targets={r['id']:r for r in m['config']['targets']}
        for r in m['records']:
            ident=r['id']
            if r['control'] or ident in oldids or ident not in targets or ident in candidates or r['mean_teacher_confidence']<.8 or r['reference_ca_error']>.02 or r['reference_encoding_parity_rmse']>.05:continue
            row=targets[ident]
            if row['family'] in families or row['sequence_sha256'] in seqs or set(row['sequence'])-set(AMINO_ACIDS):continue
            candidates[ident]=dict(row,source_labels=str(lp),source_manifest=str(mp),mean_teacher_confidence=r['mean_teacher_confidence'],reference_ca_error=r['reference_ca_error'],reference_encoding_parity_rmse=r['reference_encoding_parity_rmse'])
    handles={};selected=[]
    try:
        for bucket,quota in (((256,128),(384,128),(512,128)) if a.size==512 else ((128,19),(256,31),(384,23),(512,23))):
            ordered=sorted((r for r in candidates.values() if r['bucket']==bucket),key=lambda r:hashlib.sha256(('2026100242:'+r['id']).encode()).hexdigest());chosen=[]
            for r in ordered:
                if r['family'] in families or r['sequence_sha256'] in seqs:continue
                lp=r['source_labels']
                if lp not in handles:handles[lp]=h5py.File(lp)
                if not bool(backbone_geometry(handles[lp][r['id']+'/reference_backbone'][:][None])['coarse_valid'][0]):continue
                chosen.append(r);families.add(r['family']);seqs.add(r['sequence_sha256'])
                if len(chosen)==quota:break
            if len(chosen)!=quota:raise ValueError('Insufficient qualified references in bucket '+str(bucket))
            selected+=chosen
        rows+=selected;refs=a.output.with_suffix('.references.h5');meta=a.output.with_suffix('.references.json')
        with h5py.File(refs,'x') as out,h5py.File(basepath.parent/'fragments.h5') as old:
            for r in rows:
                source=old['train/'+r['id']] if r['id'] in oldids else handles[r['source_labels']][r['id']];g=out.create_group(r['id'])
                for key in ('reference_backbone','reference_z'):g.create_dataset(key,data=source[key][:])
        meta.write_text(json.dumps(dict(status='complete',targets=rows,source_shards=sources),indent=2)+'\n');c.update(expanded_fragment_data=True,training_targets=rows,base_training_ids=sorted(oldids),training_protein_count=a.size,work_cap_seconds=780 if a.size==512 else 540)
        for key,path in [('training_manifest',meta),('training_labels',refs),('expanded_protocol',protocol_path),('base_manifest',basepath),('base_fragments',basepath.parent/'fragments.h5'),('pool_inventory',invpath)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
        audit_sources(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print(f'Prepared{len(rows)}reference targets,{len(selected)}new and{len(oldids)}unchanged')
    finally:
        for f in handles.values():f.close()

if __name__=='__main__':main()
