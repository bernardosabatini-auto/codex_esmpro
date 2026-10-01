"""Complete the panel with family-disjoint low experimental-dispersion controls."""
import argparse,hashlib,json
from pathlib import Path
from audit_ensemble_families import hits


def main():
    p=argparse.ArgumentParser()
    for name in ('catalog','panel','self-hits','locked-hits','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('frozen panel already exists')
    rows=[r for r in json.loads(a.catalog.read_text())['targets'] if r['within_length_limit']];parent={r['query_id']:r['query_id'] for r in rows}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):
        x,y=find(x),find(y);parent[max(x,y)]=min(x,y)
    cases={}
    for row in rows:
        if row['id'] in cases:union(row['query_id'],cases[row['id']])
        else:cases[row['id']]=row['query_id']
    for q,t,*_ in hits(a.self_hits):union(q,t)
    panel=json.loads(a.panel.read_text());used=set()
    for row in panel['development']+panel['confirmation']:
        family=find(row['query_id'])
        if family in used:raise ValueError('new control sequences merged frozen panel families; re-audit before prediction')
        used.add(family);row['family']=family
    blocked={find(q) for q,*_ in hits(a.locked_hits)}
    if used&blocked:raise ValueError('frozen family overlaps locked test')
    selected=[]
    ordered=sorted([r for r in rows if r['category']=='nmr_control'],key=lambda r:hashlib.sha256(('ensemble-controls-20261001:'+r['query_id']).encode()).hexdigest())
    for row in ordered:
        family=find(row['query_id'])
        if family in used or family in blocked:continue
        used.add(family);selected.append(dict(**row,family=family,inherited_overlap_status='not yet audited; no unseen-training-family claim'))
    if len(selected)<24:raise ValueError('fewer than sixteen development plus eight confirmation control families')
    panel['confirmation']+=selected[:8];panel['development']+=selected[8:24]
    panel.update(status='frozen',pending=None,control_interpretation='Low NMR model dispersion, not measured dynamical rigidity or equilibrium populations',control_candidates=len(ordered),eligible_control_families=len(selected))
    panel['sources'].update({str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (a.catalog,a.panel,a.self_hits,a.locked_hits)})
    a.output.write_text(json.dumps(panel,indent=2)+'\n')
    print(json.dumps(dict(development=len(panel['development']),confirmation=len(panel['confirmation']))))


if __name__=='__main__':main()
