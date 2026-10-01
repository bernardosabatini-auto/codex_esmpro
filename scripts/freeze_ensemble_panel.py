"""Reserve families using only experimental references, before model predictions."""
import argparse,hashlib,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    for name in ('mapped','audit','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();mapped=json.loads(a.mapped.read_text());audit=json.loads(a.audit.read_text())
    if audit['status']!='complete' or a.output.exists():raise ValueError('require completed audit and a new output')
    clusters=audit['clusters'];blocked=set(audit['blocked_clusters']);used=set();eligible=[]
    # Deterministic ordering is frozen independently of generated-model quality.
    order=lambda r:hashlib.sha256(('ensemble-panel-20261001:'+r['query_id']).encode()).hexdigest()
    for row in sorted(mapped['mapped'],key=order):
        family=clusters[row['query_id']]
        if family in blocked or family in used:continue
        used.add(family)
        eligible.append(dict(**row,family=family,inherited_overlap=audit['inherited_overlap'].get(row['query_id'])))
    if len(eligible)<24:raise ValueError('need sixteen development and eight reserved families')
    # Reserve first, then select development; no model outputs enter this script.
    confirmation=eligible[:8];development=eligible[8:24]
    md=[]
    for row in sorted(mapped['md_candidates'],key=order):
        family=clusters[row['query_id']]
        if family in blocked or family in {r['family'] for r in confirmation+development+md}:continue
        md.append(dict(**row,family=family,inherited_overlap=audit['inherited_overlap'].get(row['query_id'])))
    if len(md)<17:raise ValueError('need seventeen disjoint MD families for planned development and reserve')
    result=dict(status='frozen_multistate_and_md',development=development+md[1:17],confirmation=confirmation+md[:1],
        pending='NMR control cohort and its family exclusion are still being curated; do not call this the complete 48-protein panel',
        selection='SHA256 ordering with fixed salt; one construct per connected family; reserve first; no predictions used',
        confirmation_limitation='Only one MD reference system reserved: insufficient for a reliable MD confirmation claim. Add an independent source before such a claim.',
        sources={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (a.mapped,a.audit)})
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(development=len(result['development']),confirmation=len(result['confirmation']))))


if __name__=='__main__':main()
