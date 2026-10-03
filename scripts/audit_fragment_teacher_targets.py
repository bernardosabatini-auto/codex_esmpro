"""Inventory cached teacher endpoints without changing any supplied fragment."""
import argparse,collections,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def proper_rmsd_batch(mobile,reference):
    x=np.asarray(mobile,dtype=np.float64);y=np.asarray(reference,dtype=np.float64)
    if x.ndim!=3 or x.shape[1:]!=y.shape or y.shape[1]!=3 or len(y)<3 or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Invalid matched CA arrays')
    x=x-x.mean(1,keepdims=True);y=y-y.mean(0)
    u,_,vt=np.linalg.svd(np.einsum('bni,nj->bij',x,y));correction=np.broadcast_to(np.eye(3),(len(x),3,3)).copy();correction[:,-1,-1]=np.linalg.det(u@vt)
    return np.sqrt(np.mean(np.sum((x@(u@correction@vt)-y)**2,axis=-1),axis=-1))


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_teacher_targets_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['data_run'];manifest=run/'manifest.json';m=json.loads(manifest.read_text());report=root/'reports'/(spec['data_run']+'.json');d=json.loads(report.read_text());c=m['config']
    if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(manifest) or not d['training_gate_passed']:raise ValueError('Unaudited fragment source')
    for key in ('training_manifest','pool_inventory'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed fragment provenance')
    sources=json.loads(Path(c['training_manifest']).read_text())['source_shards'];bound={s['labels']:s for s in sources};handles={};rows=[];target_rows=c['training_targets']
    if len(target_rows)!=512:raise ValueError('Changed training denominator')
    # The expanded inventory omits the original32's four immutable source shards.
    for r in target_rows:
        source=r['source_labels']
        if source in bound:continue
        expected={v.get('source_labels_sha256') for v in target_rows if v['source_labels']==source}
        path=Path(source).parent/'manifest.json';old=json.loads(path.read_text())
        if len(expected)!=1 or None in expected or old['status']!='complete':raise ValueError('Unbound original teacher shard')
        entry=dict(labels=source,labels_sha256=expected.pop(),manifest=str(path),manifest_sha256=sha(path));bound[source]=entry;sources.append(entry)
    try:
        for s in sources:
            if sha(s['manifest'])!=s['manifest_sha256'] or sha(s['labels'])!=s['labels_sha256']:raise ValueError('Changed cached teacher source')
        with h5py.File(run/'fragments.h5') as fr:
            if set(fr['train'])!={r['id'] for r in target_rows}:raise ValueError('Changed training inventory')
            for r in target_rows:
                source=r['source_labels']
                if source not in bound:raise ValueError('Unregistered cached teacher shard')
                if source not in handles:handles[source]=h5py.File(source)
                g=handles[source][r['id']];original=fr['train/'+r['id']];n=r['length']
                if str(g.attrs['sequence_sha256'])!=r['sequence_sha256'] or not np.array_equal(g['reference_backbone'][:],original['reference_backbone'][:]) or not np.array_equal(g['reference_z'][:],original['reference_z'][:]):raise ValueError('Source reference or sequence differs: '+r['id'])
                bb=g['teacher_backbone'][:];z=g['teacher_z'][:];confidence=g['teacher_plddt'][:];valid=g['coarse_valid'][:]
                if bb.shape!=(16,n,4,3) or z.shape!=(16,n,8) or confidence.shape!=(16,n) or valid.shape!=(16,) or not all(np.isfinite(v).all() for v in (bb,z,confidence)):raise ValueError('Changed cached state inventory')
                confidence=confidence.mean(1);state_ok=valid.astype(bool)&(confidence>=spec['minimum_mean_plddt'])
                if len(original['conditions'])!=9:raise ValueError('Changed condition inventory')
                for name,q in original['conditions'].items():
                    fragment=q['fragment'][:,1];start=int(q.attrs['start']);x=bb[:,start:start+len(fragment),1];proper=proper_rmsd_batch(x,fragment);distance=np.linalg.norm(fragment[:,None]-fragment[None],axis=-1);accepted=[]
                    for index in np.flatnonzero(state_ok&(proper<=spec['maximum_proper_rmsd'])):
                        pair=np.linalg.norm(x[index,:,None]-x[index,None,:],axis=-1);drms=float(np.sqrt(np.mean((pair-distance)**2)))
                        if drms<=spec['maximum_drms']:accepted.append(dict(index=int(index),proper_rmsd=float(proper[index]),drms=drms,mean_plddt=float(confidence[index])))
                    rows.append(dict(target_id=r['id'],bucket=r['bucket'],condition=name,length=n,motif_start=start,motif_length=len(fragment),source_labels=source,eligible_states=accepted))
        eligible=[r for r in rows if r['eligible_states']];buckets={str(b):dict(total=sum(r['bucket']==b for r in rows),eligible=sum(r['bucket']==b for r in eligible)) for b in (128,256,384,512)};center=[r for r in rows if r['condition']=='f30_center'];proteins=len({r['target_id'] for r in eligible});center_fraction=sum(bool(r['eligible_states']) for r in center)/len(center)
        gate=proteins>=spec['minimum_proteins'] and len(eligible)/len(rows)>=spec['minimum_condition_fraction'] and center_fraction>=spec['minimum_center30_fraction'] and all(v['eligible']/v['total']>=spec['minimum_bucket_condition_fraction'] for v in buckets.values())
        result=dict(status='complete',protocol_sha256=sha(protocol),source_manifest_sha256=sha(manifest),fragments_sha256=sha(run/'fragments.h5'),source_shards=sources,conditions=len(rows),eligible_conditions=len(eligible),eligible_proteins=proteins,eligible_center30_fraction=center_fraction,buckets=buckets,state_count_histogram=dict(collections.Counter(len(r['eligible_states']) for r in rows)),feasibility_gate_passed=gate,records=rows)
        a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');summary={k:v for k,v in result.items() if k not in ('records','source_shards')};a.output.with_suffix('.md').write_text('# Cached compatible teacher targets\n\nTraining-only feasibility; no new GPU labels, target replacement, or designability claim.\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n');print(json.dumps(summary))
    finally:
        for f in handles.values():f.close()


if __name__=='__main__':main()
