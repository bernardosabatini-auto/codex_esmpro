"""Audit construct-level family overlap before any generated ensemble selection."""
import argparse
import hashlib
import json
from pathlib import Path


def hits(path):
    for line in path.read_text().splitlines():
        q,t,identity,qcov,tcov=line.split('\t')
        if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:
            yield q,t,float(identity),float(qcov),float(tcov)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('catalog','self-hits','locked-hits','inherited-hits','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();rows=[r for r in json.loads(a.catalog.read_text())['targets'] if r['within_length_limit']]
    parent={r['query_id']:r['query_id'] for r in rows}
    if len(parent)!=len(rows):raise ValueError('duplicate construct identifiers')
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):
        x,y=find(x),find(y);parent[max(x,y)]=min(x,y)
    # Same biological case remains a single unit even if construct overlap is short.
    by_case={}
    for r in rows:
        key=r['id']
        if key in by_case:union(r['query_id'],by_case[key])
        else:by_case[key]=r['query_id']
    for q,t,*_ in hits(a.self_hits):union(q,t)
    clusters={q:find(q) for q in parent}
    locked={};inherited={}
    for q,t,*values in hits(a.locked_hits):locked.setdefault(q,[]).append(dict(target=t,values=values))
    for q,t,*values in hits(a.inherited_hits):
        if q not in parent:raise ValueError('unknown construct')
        source=t.split('|')[0]
        entry=inherited.setdefault(q,dict(sources={},examples=[]))
        entry['sources'][source]=entry['sources'].get(source,0)+1
        if len(entry['examples'])<5:entry['examples'].append(dict(target=t,values=values))
    blocked={clusters[q] for q in locked}
    result=dict(status='complete',protocol='MMseqs sensitive search; identity >=30%, coverage >=50% on either sequence; connected components plus biological-case identity',
        clusters=clusters,locked_overlap=locked,blocked_clusters=sorted(blocked),inherited_overlap=inherited,
        input_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (a.catalog,a.self_hits,a.locked_hits,a.inherited_hits)},
        caveat='Inherited corpus includes training and prior development. Report sources separately; no independence claim from an absence of exact matches.')
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(constructs=len(rows),families=len(set(clusters.values())),locked_overlap=len(locked),inherited_overlap=len(inherited))))


if __name__=='__main__':main()
