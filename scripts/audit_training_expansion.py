"""Refresh sequence-only exclusions for unused inherited training candidates."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from prepare_overfit import sha
from prepare_holdout import fasta


def components(ids, text):
    parent={i:i for i in ids}
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for line in text.splitlines():
        q,t,identity,qcov,tcov=line.split('\t')
        if q not in parent or t not in parent:raise ValueError('self-search contains unknown ID')
        if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:parent[root(q)]=root(t)
    grouped={}
    for i in ids:grouped.setdefault(root(i),[]).append(i)
    return {i:min(members) for members in grouped.values() for i in members}


def eligible(rows, groups, hits, occupied):
    excluded=set(groups[i] for i in occupied)
    for line in hits.splitlines():
        q,t,identity,qcov,tcov=line.split('\t')
        if q not in groups:raise ValueError('external search contains unknown query')
        if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:excluded.add(groups[q])
    chosen=[]
    for family in sorted(set(groups.values())-excluded):
        # Representative depends only on sequence IDs; no model outcomes.
        r=rows[min(i for i in rows if groups[i]==family)]
        if len(r['sequence'])!=r['length'] or hashlib.sha256(r['sequence'].encode()).hexdigest()!=r['sequence_sha256']:raise ValueError('candidate sequence mismatch')
        if not set(r['sequence'])<=set('ACDEFGHIKLMNPQRSTVWY'):continue
        chosen.append(dict(r,family=family))
    return chosen


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--mmseqs',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    frozen=root/'runs/layer_probe/frozen.json';selection=json.loads(frozen.read_text())
    for path,digest in selection['source_sha256'].items():
        if sha(root/path)!=digest:raise ValueError('original sequence audit changed')
    poolpath=root/'runs/layer_probe/pool.json';pool=json.loads(poolpath.read_text());rows={r['id']:r for r in pool['records']}
    if len(rows)!=2048 or len(selection['train'])!=512 or len(selection['tuning'])!=64 or len(selection['confirmation'])!=64:raise ValueError('unexpected existing split')
    source_paths=[frozen,poolpath,root/'runs/layer_probe/self.tsv',root/'runs/layer_probe/reference_exclusion.fasta',root/'runs/ensemble_sources/candidate_catalog_v2.json',root/'runs/holdout_expanded_20260930/locked_test.json']
    groups=components(rows,(root/'runs/layer_probe/self.tsv').read_text())
    excluded={seq for _,seq in fasta(root/'runs/layer_probe/reference_exclusion.fasta')}
    for path in (frozen,*source_paths[-2:]):
        data=json.loads(path.read_text())
        for split in ('train','tuning','confirmation','targets'):
            excluded.update(r['sequence'] for r in data.get(split,[]))
    a.output.mkdir(parents=True,exist_ok=False)
    query=a.output/'pool.fasta';query.write_text(''.join(f'>{i}\n{rows[i]["sequence"]}\n' for i in sorted(rows)))
    database=a.output/'exclusion.fasta';database.write_text(''.join(f'>excluded_{i}\n{s}\n' for i,s in enumerate(sorted(excluded))))
    hitpath=a.output/'hits.tsv'
    command=[str(a.mmseqs),'easy-search',str(query),str(database),str(hitpath),str(a.output/'tmp'),'-s','7.5','-e','1e-3','--max-seqs','10000','--threads','1','--split-memory-limit','4G','--format-output','query,target,fident,qcov,tcov','-v','1']
    manifest=dict(status='running',scope='Sequence-only training candidate audit. No model or structural-reference scoring, no GPU use, no added labels. Inherited checkpoint training overlap persists.',sources={str(p):sha(p) for p in source_paths},mmseqs_sha256=sha(a.mmseqs),command=command,source_candidates=len(rows),source_components=len(set(groups.values())),exclusion_sequences=len(excluded),rule='Sensitive MMseqs search; exclude identity>=30% with coverage>=50% on either sequence, then propagate through existing self-search components. This is a heuristic sequence exclusion, not proof of evolutionary independence.')
    path=a.output/'manifest.json';path.write_text(json.dumps(manifest,indent=2)+'\n')
    try:
        with (a.output/'search.log').open('w') as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=900)
        occupied={r['id'] for split in ('train','tuning','confirmation') for r in selection[split]}
        chosen=eligible(rows,groups,hitpath.read_text(),occupied)
        candidate=dict(status='candidate_inventory',dataset=pool['dataset'],train=chosen,source_audit=str(path.resolve()),scope='Unused inherited training families only. All require exact source-backbone verification, fresh matching ESMC embeddings, teacher generation and reconstruction certification before use. No new model-training configuration is created.')
        candidate_path=a.output/'candidates.json';candidate_path.write_text(json.dumps(candidate,indent=2)+'\n')
        manifest.update(status='complete',candidates=len(chosen),candidate_families=len({r['family'] for r in chosen}),buckets=dict(Counter(r['bucket'] for r in chosen)),candidate_manifest=str(candidate_path.resolve()),candidate_manifest_sha256=sha(candidate_path),hits_sha256=sha(hitpath))
    except BaseException as error:manifest.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('status','source_candidates','source_components','exclusion_sequences','candidates','buckets')}))


if __name__=='__main__':main()
