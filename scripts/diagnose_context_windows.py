"""Search all existing training20-residue windows on CPU, without new labels."""
import argparse
import json
import time
from pathlib import Path
import h5py
import numpy as np
from diagnose_context_retrieval import proper_distances
from prepare_overfit import sha

PAIR = np.triu_indices(20,1)


def rank(row):
    return (row['score'],row['ca_rmsd'],row['drms'],row['id'],row['start'])


def update_neighbors(top, windows, distances, donor, query, query_distances):
    """Exact branch bound: joint max(RMSD,dRMS) cannot be below dRMS."""
    drms=np.sqrt(np.mean((distances-query_distances)**2,axis=1)*.95)
    threshold=max(z['score'] for z in top.values()) if len(top)==4 else np.inf
    possible=np.flatnonzero(drms<=threshold)
    if len(possible):
        rmsd=proper_distances(windows[possible],query)
        options=[dict(**donor,start=int(i),ca_rmsd=float(rms),drms=float(drms[i]),score=float(max(rms,drms[i]))) for i,rms in zip(possible,rmsd)]
        best=min(options,key=rank);family=donor['family']
        if family not in top or rank(best)<rank(top[family]):top[family]=best
        top={z['family']:z for z in sorted(top.values(),key=rank)[:4]}
    return top


def main():
    p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();tick=time.monotonic();dm=a.data/'manifest.json';data=json.loads(dm.read_text())
    cm=a.corpus/'manifest.json';corpus=json.loads(cm.read_text());source=a.corpus/'fragments.h5'
    if corpus['status']!='complete' or not corpus['training_gate_passed'] or sha(source)!=corpus['fragments_sha256']:
        raise ValueError('Certified immutable training corpus required')
    if sha(data['arrays'])!=data['arrays_sha256']:raise ValueError('Changed supplied queries')
    excluded={r['family'] for r in data['records'] if r['split']!='train'}
    evaluation=[r for r in data['records'] if r['split']=='evaluation']
    with np.load(data['arrays'],allow_pickle=False) as z:
        query=z['evaluation_features'][:,:,28:].reshape(-1,20,4,3)[:,:,1].astype(float)*10
    qd=np.linalg.norm(query[:,PAIR[0]]-query[:,PAIR[1]],axis=-1)
    best={r['id']:{} for r in evaluation};count=0;windows_count=0
    with h5py.File(source) as f:
        for ident in sorted(f['train']):
            g=f['train/'+ident];family=str(g.attrs['family'])
            if family in excluded:continue
            ca=np.asarray(g['reference_backbone'][:,1],dtype=float);n=len(ca);bucket=((n+127)//128)*128
            if not np.isfinite(ca).all() or n<20:raise ValueError('Invalid verified source')
            windows=np.lib.stride_tricks.sliding_window_view(ca,20,axis=0).transpose(0,2,1)
            distances=np.linalg.norm(windows[:,PAIR[0]]-windows[:,PAIR[1]],axis=-1)
            donor=dict(id=ident,family=family,length=n,bucket=bucket)
            for r in evaluation:
                if r['bucket']!=bucket:continue
                best[r['id']]=update_neighbors(best[r['id']],windows,distances,donor,query[r['index']],qd[r['index']])
            count+=1;windows_count+=len(windows)
            if count%1000==0:print('searched',count,'proteins',windows_count,'windows',flush=True)
    rows=[]
    for r in evaluation:
        values=sorted(best[r['id']].values(),key=rank)
        if len(values)!=4:raise ValueError('Missing distinct donor families')
        rows.append(dict(target_id=r['id'],family=r['family'],bucket=r['bucket'],neighbors=values))
    summary=dict(library_proteins=count,library_windows=windows_count,query_families=len(evaluation),
        queries_with_neighbor_under1A=sum(r['neighbors'][0]['score']<=1 for r in rows),
        slots_under1A=sum(z['score']<=1 for r in rows for z in r['neighbors']),
        median_nearest_score=float(np.median([r['neighbors'][0]['score'] for r in rows])),elapsed_seconds=time.monotonic()-tick)
    result=dict(status='complete',scope='Exploratory CPU input geometry only. All contiguous20-residue windows in certified training sources, matched length bucket, four distinct donor families; minimize max(properCA RMSD,dRMS). Excludes all context-flow evaluation and validation families. No new generation, training or designability claim.',
                corpus_manifest_sha256=sha(cm),fragments_sha256=corpus['fragments_sha256'],data_manifest_sha256=sha(dm),summary=summary,rows=rows)
    with a.output.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(summary))


if __name__=='__main__':main()
