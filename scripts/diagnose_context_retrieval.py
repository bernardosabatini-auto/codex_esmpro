"""CPU-only availability of training motifs; no model outputs select neighbors."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha


def proper_distances(candidates, query):
    x=np.asarray(candidates,dtype=np.float64);y=np.asarray(query,dtype=np.float64)
    x=x-x.mean(1,keepdims=True);y=y-y.mean(0,keepdims=True)
    u,_,v=np.linalg.svd(np.einsum('nki,kj->nij',x,y))
    u[:,:,-1]*=np.linalg.det(u@v)[:,None]
    rotation=u@v
    return np.sqrt(np.mean(np.sum((x@rotation-y)**2,axis=-1),axis=-1))


def main():
    p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True)
    p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();data_path=a.data/'manifest.json';data=json.loads(data_path.read_text())
    cm=a.corpus/'manifest.json';corpus=json.loads(cm.read_text());source=a.corpus/'fragments.h5'
    if corpus['status']!='complete' or not corpus['training_gate_passed'] or sha(source)!=corpus['fragments_sha256']:
        raise ValueError('A completed certified training corpus is required')
    excluded={r['family'] for r in data['records'] if r['split']!='train'}
    evaluation=[r for r in data['records'] if r['split']=='evaluation']
    with np.load(data['arrays'],allow_pickle=False) as z:
        if sha(data['arrays'])!=data['arrays_sha256']:raise ValueError('Changed isolated inputs')
        query=z['evaluation_features'][:,:,28:].reshape(-1,20,4,3)[:,:,1].astype(np.float64)*10
    library=[];metadata=[]
    with h5py.File(source) as f:
        for ident in sorted(f['train']):
            g=f['train/'+ident];family=str(g.attrs['family'])
            if family in excluded:continue
            q=g['conditions/c20_center'];n=len(g['reference_z']);bb=q['fragment'][:]
            if bb.shape!=(20,4,3) or not np.isfinite(bb).all():raise ValueError('Invalid certified fragment')
            metadata.append(dict(id=ident,family=family,length=n,bucket=((n+127)//128)*128,start=int(q.attrs['start'])))
            library.append(bb[:,1])
    library=np.stack(library);rows=[]
    for r in evaluation:
        distances=proper_distances(library,query[r['index']])
        candidates=[i for i,z in enumerate(metadata) if z['bucket']==r['bucket']]
        candidates.sort(key=lambda i:(distances[i],metadata[i]['family'],metadata[i]['id']))
        chosen=[];seen=set();qd=np.linalg.norm(query[r['index']][:,None]-query[r['index']][None],axis=-1)
        for i in candidates:
            z=metadata[i]
            if z['family'] in seen:continue
            seen.add(z['family']);ld=np.linalg.norm(library[i,:,None]-library[i,None,:],axis=-1)
            drms=float(np.sqrt(np.mean((ld-qd)**2)))
            chosen.append(dict(**z,ca_rmsd=float(distances[i]),drms=drms))
            if len(chosen)==4:break
        if len(chosen)!=4:raise ValueError('Insufficient distinct donor families')
        rows.append(dict(target_id=r['id'],family=r['family'],bucket=r['bucket'],neighbors=chosen))
    # Geometric availability is not a prediction of refolding or designability.
    summary=dict(library_proteins=len(metadata),query_families=len(evaluation),
        queries_with_neighbor_under1A=sum(any(z['ca_rmsd']<=1 and z['drms']<=1 for z in r['neighbors']) for r in rows),
        slots_under1A=sum(z['ca_rmsd']<=1 and z['drms']<=1 for r in rows for z in r['neighbors']),
        median_nearest_rmsd=float(np.median([r['neighbors'][0]['ca_rmsd'] for r in rows])))
    result=dict(status='complete',scope='Exploratory CPU input-geometry availability; center motifs, matched length buckets, four distinct training donor families. No GPU or generation, no validation/evaluation donor families, no designability claim.',
                corpus_manifest_sha256=sha(cm),fragments_sha256=corpus['fragments_sha256'],data_manifest_sha256=sha(data_path),summary=summary,rows=rows)
    with a.output.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(summary))


if __name__=='__main__':main()
