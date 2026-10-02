"""Freeze a metadata-only generation profile and historical positive controls."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from expansion_data import profile_rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    selection=root/'runs/expansion_candidates_20261002/candidates.json';inventory=json.loads(selection.read_text())
    audit=Path(inventory['source_audit']);audit_data=json.loads(audit.read_text())
    native=root/'runs/expansion_sources_20261002/manifest.json';sources=json.loads(native.read_text())
    if audit_data['status']!='complete' or audit_data['candidate_manifest_sha256']!=sha(selection) or sources['status']!='complete' or sources['selection_sha256']!=sha(selection):raise ValueError('source audit changed/incomplete')
    if len(sources['records'])!=len(inventory['train']) or {r['id'] for r in sources['records']}!={r['id'] for r in inventory['train']}:raise ValueError('incomplete source verification')
    oldselection=root/'runs/layer_probe/frozen.json';old=json.loads(oldselection.read_text());oldrows={r['id']:r for r in old['train']}
    historical={}
    training=json.loads((root/'runs/distillation_49654703/manifest.json').read_text())
    for shard in training['config']['label_shards']:
        aligned=json.loads(Path(shard['manifest']).read_text());rawpath=Path(aligned['config']['source_manifest']);raw=json.loads(rawpath.read_text())
        if raw['status']!='complete' or sha(rawpath)!=aligned['config']['source_manifest_sha256']:raise ValueError('raw historical source changed')
        labels=rawpath.parent/'labels.h5'
        if sha(labels)!=aligned['config']['source_labels_sha256']:raise ValueError('raw label arrays changed')
        for r in raw['records']:historical[r['id']]=dict(raw_manifest=str(rawpath),raw_manifest_sha256=sha(rawpath),raw_labels=str(labels),raw_labels_sha256=aligned['config']['source_labels_sha256'])
    controls=[]
    for bucket in (128,256,384,512):
        r=max((r for r in oldrows.values() if r['bucket']==bucket),key=lambda r:(r['length'],r['id']))
        controls.append(dict(r,**historical[r['id']],control=True))
    raw=json.loads(Path(controls[0]['raw_manifest']).read_text())
    ec=root/'runs/layer_probe_49625917/manifest.json';em=json.loads(ec.read_text())
    fields=dict(protocol=root/'configs/expansion_data_protocol.json',selection=selection,source_audit=audit,native_manifest=native,native_backbones=Path(sources['dataset']),old_selection=oldselection,old_native_backbones=root/'runs/teacher_training_sources/backbones.h5',old_embedding_cache=ec.parent/'embeddings.h5',embedding_manifest=ec,decoder_checkpoint=Path(em['decoder_checkpoint']['path']))
    c=dict(phase='profile',targets=[dict(r,control=False) for r in profile_rows(inventory['train'])],controls=controls,seed=2026100121,work_cap_seconds=1080,latent_frame='teacher_CA_aligned_to_cached_reference',teacher_artifacts=raw['config']['teacher_artifacts'],embedding_artifacts=em['embedding_artifacts'])
    for key,path in fields.items():c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    for artifact in c['teacher_artifacts']+c['embedding_artifacts']:
        s=Path(artifact['path']).stat()
        if s.st_size!=artifact['bytes'] or s.st_mtime_ns!=artifact['mtime_ns']:raise ValueError('historical model artifact changed')
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(config=str(a.output),new_targets=len(c['targets']),controls=len(controls))))


if __name__=='__main__':main()
