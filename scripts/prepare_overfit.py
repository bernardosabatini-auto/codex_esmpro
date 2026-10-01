"""Freeze 32 diverse training-only ensembles without inspecting student outcomes."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from latentfold.teacher_states import definition


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/overfit_protocol.json'));a=p.parse_args();recipe=json.loads(a.protocol.read_text());reliable=recipe.get('panel')=='confident_multistate'
    source=Path('runs/distillation_49654703/manifest.json');m=json.loads(source.read_text());c=m['config'];selection=json.loads(Path(c['selection']).read_text());rows={r['id']:r for r in selection['train']}
    if m['status']!='complete' or sha(c['selection'])!=c['selection_sha256']:raise ValueError('invalid frozen source')
    candidates=[]
    for shard in c['label_shards']:
        path=Path(shard['manifest']);metadata=json.loads(path.read_text());labels=path.parent/'labels.h5'
        if sha(path)!=shard['manifest_sha256'] or sha(labels)!=shard['labels_sha256'] or metadata['status']!='complete':raise ValueError('changed source')
        with h5py.File(labels) as h:
            for ident in sorted(h):
                g=h[ident];confidence=g['teacher_plddt'][:];mean_confidence=float(confidence.mean())
                if reliable and (mean_confidence<.8 or (confidence.mean(0)>=.7).sum()<max(32,np.ceil(rows[ident]['length']/2))):continue
                d=definition(g['teacher_backbone'][:],g['coarse_valid'][:],confidence)
                if reliable and d is not None and (d['states']>8 or d['mean_pair_distance']>6):continue
                if d is not None and d['states']>=2:
                    candidates.append(dict(**rows[ident],source_labels=str(labels.resolve()),source_labels_sha256=shard['labels_sha256'],state_definition=d,mean_teacher_confidence=mean_confidence))
        print('scanned',path.parent.name,'eligible',len(candidates),flush=True)
    chosen=[]
    for bucket in (128,256,384,512):
        eligible=sorted([r for r in candidates if r['bucket']==bucket],key=lambda r:(-r['mean_teacher_confidence'],r['id']) if reliable else (-r['state_definition']['states'],-r['state_definition']['mean_pair_distance'],r['id']))
        count=recipe.get('selection_counts',{}).get(str(bucket),8)
        if len(eligible)<count:raise ValueError(f'only {len(eligible)} eligible targets in bucket {bucket}')
        chosen+=eligible[:count]
    protocol=a.protocol
    d=dict(status='complete',selection=c['selection'],selection_sha256=c['selection_sha256'],embedding_cache=c['embedding_cache'],source_manifest=str(source.resolve()),source_manifest_sha256=sha(source),protocol=str(protocol.resolve()),protocol_sha256=sha(protocol),targets=chosen,candidates=len(candidates),scope='Training-only capacity test, teacher-defined modes are not experimentally established states',work_cap_seconds=780,seed=2026100161)
    a.output.write_text(json.dumps(d,indent=2)+'\n');print('selected',len(chosen),flush=True)

if __name__=='__main__':main()
