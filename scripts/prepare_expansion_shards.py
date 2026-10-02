"""Expand only a qualified fixed profile; disjoint new families, identical recipe."""
import argparse,json,math
from pathlib import Path
from expansion_data import profile_rows
from prepare_overfit import sha
from summarize_expansion_data import summarize


def partition(rows,used,shards=4):
    ids={r['id'] for r in rows}
    if len(ids)!=len(rows) or not set(used)<=ids:raise ValueError('invalid candidate partition')
    groups=[[] for _ in range(shards)]
    for bucket in (128,256,384,512):
        remaining=sorted((r for r in rows if r['bucket']==bucket and r['id'] not in used),key=lambda r:(-r['length'],r['id']))
        # Snake assignment balances both counts and length within each bucket.
        for index,r in enumerate(remaining):
            block,slot=divmod(index,shards);groups[slot if block%2==0 else shards-1-slot].append(r)
    assigned=[r['id'] for group in groups for r in group]
    if len(set(assigned))!=len(assigned) or set(assigned)|set(used)!=ids or set(assigned)&set(used):raise ValueError('incomplete or overlapping partition')
    return groups


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    m=json.loads(a.profile.read_text());report=summarize(m);c=m['config'];selection=json.loads(Path(c['selection']).read_text())
    if not report['generation_qualified'] or c['phase']!='profile':raise ValueError('generation profile not qualified')
    if report['reconstruction']['targets'] and not report['reconstruction']['gate_passed']:raise ValueError('profile label reconstruction failed; investigate before expansion')
    if c['targets']!=[dict(r,control=False) for r in profile_rows(selection['train'])]:raise ValueError('profile selected different families')
    for key in ('labels','embeddings'):
        if sha(a.profile.parent/(key+'.h5'))!=m[key+'_sha256']:raise ValueError('profile output changed')
    for key in ('selection','source_audit','native_manifest','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed frozen data input')
    groups=partition(selection['train'],[r['id'] for r in c['targets']]);paths=[];estimates=[]
    # Conservative bucket-wise worst observed seconds per new family, plus
    # measured loading/control overhead, with50% margin. Bound each at60minutes.
    rates={b:sum(max(x['seconds'] for x in m['batches'] if x['phase']==phase and x.get('bucket')==b and not x.get('control',False)) for phase in ('teacher','encode_audit')) for b in (128,256,384,512)}
    embedding_rate=max(x['seconds']/x['batch'] for x in m['batches'] if x['phase']=='embedding')
    for index,rows in enumerate(groups):
        estimate=1.5*(sum(rates[r['bucket']]+embedding_rate for r in rows)+m['elapsed_seconds'])
        if estimate>3300:raise ValueError('measured throughput does not fit a55minute work budget')
        config=dict(c,phase='expansion',shard=index,targets=[dict(r,control=False) for r in rows],work_cap_seconds=3300,profile_manifest=str(a.profile.resolve()),profile_manifest_sha256=sha(a.profile))
        path=a.output.with_name(f'{a.output.stem}_{index}.json');path.write_text(json.dumps(config,indent=2)+'\n');paths.append(str(path));estimates.append(estimate)
    print(json.dumps(dict(configs=paths,counts=[len(x) for x in groups],conservative_seconds=estimates,reuse_profile_targets=len(c['targets']))))


if __name__=='__main__':main()
