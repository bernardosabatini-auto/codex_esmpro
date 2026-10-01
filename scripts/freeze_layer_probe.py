"""Select family-isolated train, tuning and confirmation for a cheap layer screen."""
import argparse,hashlib,json
from pathlib import Path
from audit_ensemble_families import hits


def main():
    p=argparse.ArgumentParser()
    for name in ('pool','self-hits','excluded-hits','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();source=json.loads(a.pool.read_text());rows=source['records'];parent={r['id']:r['id'] for r in rows}
    if a.output.exists():raise ValueError('selection already frozen')
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for q,t,*_ in hits(a.self_hits):
        q,t=find(q),find(t);parent[max(q,t)]=min(q,t)
    blocked={find(q) for q,*_ in hits(a.excluded_hits)};used=set();result=dict(status='frozen',dataset=source['dataset'],train=[],tuning=[],confirmation=[],exclusion='All reference candidates, reserved confirmation, and original locked-test sequences; >=30% identity and >=50% coverage on either sequence',scope='Fresh linear representation probes. Source records were inherited training data; this does not establish unseen-family generalization for the inherited flow checkpoint.',source_sha256={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (a.pool,a.self_hits,a.excluded_hits)})
    for bucket in (128,256,384,512):
        candidates=sorted([r for r in rows if r['bucket']==bucket],key=lambda r:hashlib.sha256(('probe-select-20261001:'+r['id']).encode()).hexdigest())
        chosen=[]
        for row in candidates:
            family=find(row['id'])
            if family in blocked or family in used:continue
            used.add(family);chosen.append(dict(**row,family=family))
            if len(chosen)==160:break
        if len(chosen)!=160:raise ValueError('insufficient isolated families in bucket '+str(bucket))
        result['confirmation']+=chosen[:16];result['tuning']+=chosen[16:32];result['train']+=chosen[32:]
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:len(result[k]) for k in ('train','tuning','confirmation')}))


if __name__=='__main__':main()
