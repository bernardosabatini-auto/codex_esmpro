"""Qualify fresh reference positives without pooling decoder/sequence attempts."""
import argparse
import json
from pathlib import Path


def ready_command(root):
    path=root/'runs/native_positive_coverage_refolds.json';output=root/'reports/native_positive_coverage_20261003'
    if not path.exists() or output.with_suffix('.json').exists():return None
    plan=json.loads(path.read_text());ids=plan['jobs']
    if len(ids)!=4 or len(set(ids))!=4:raise ValueError('Expected four reference partitions')
    registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if any(i not in registry or registry[i]['completion_action']!='summarize_fragment_preference_refold' for i in ids):raise ValueError('Unregistered reference qualification job')
    reports=[root/f'reports/fragment_preference_refold_{i}.json' for i in ids]
    if not all(p.exists() and json.loads(p.read_text())['status']=='complete' for p in reports):return None
    if any(json.loads(p.read_text())['generation_manifest_sha256']!=plan['generation_manifest_sha256'] for p in reports):raise ValueError('Changed declared native generation')
    return [str(root/'scripts/compare_native_positive_coverage.py'),'--plan',str(path),'--output',str(output)]


def compare(plan,root):
    from native_positive_coverage import audit_refold,analyze_generation,qualify_sources
    from prepare_overfit import sha
    records=[];sources=[];parts=set();generation=None;gc=None;spec=None
    for jid in plan['jobs']:
        run=root/f'runs/fragment_preference_refold_{jid}';mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json')
        m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];this_gc,this_spec=audit_refold(c)
        if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp)
                or d['refolded_sha256']!=sha(run/'refolded.h5') or d['completed_refolds']!=256
                or len(d['records'])!=32 or c['partition'] in parts or d['partition']!=c['partition']
                or d['generation_manifest_sha256']!=plan['generation_manifest_sha256']
                or [r['name'] for r in d['records']]!=[r['name'] for r in c['entries']]):raise ValueError('Incomplete or changed reference partition')
        if gc is not None and (this_gc!=gc or this_spec!=spec):raise ValueError('Mixed reference generations')
        gc,spec=this_gc,this_spec;parts.add(c['partition']);records.extend(d['records']);sources.append(dict(path=str(rp),sha256=sha(rp)))
        generation=c['generation_manifest'];generation_report=c['generation_report']
    if parts!=set(range(4)):raise ValueError('Incomplete partition coverage')
    gd=analyze_generation(Path(generation).parent);stored=json.loads(Path(generation_report).read_text())
    if gd!=stored or not gd['native_generation_gate']:raise ValueError('Generation audit not reproducible')
    gate,rows=qualify_sources(records,gd['native_records'],gc['selected'],spec['label_gate'])
    return dict(status='complete',protocol=gc['protocol'],protocol_sha256=sha(gc['protocol']),source_reports=sources,
                generation_manifest=generation,generation_manifest_sha256=sha(generation),generation_report=generation_report,generation_report_sha256=sha(generation_report),
                proteins=64,decoded_backbones=128,refolds=1024,raw_both_qualified=gd['native_raw_both_qualified'],
                gate=gate,rows=rows,strong_decodes=sum(r['scaffold_joint_success'] for r in records),designable_decodes=sum(r['valid_designable'] for r in records),
                by_length=[dict(bucket=b,proteins=sum(r['bucket']==b for r in rows),qualified=sum(r['bucket']==b and r['qualified'] for r in rows)) for b in (128,256,384,512)],
                scope='Training-source reference-positive qualification only. Both decoder realizations must separately pass strict raw/full-reference and same-valid-refold motif/global/scaffold criteria. No pooling, outcome-based source selection, or model improvement claim.')


def main():
    import fcntl
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    with a.output.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if a.output.with_suffix('.json').exists():return
        d=compare(json.loads(a.plan.read_text()),Path(__file__).resolve().parents[1]);temporary=a.output.with_suffix('.json.tmp');temporary.write_text(json.dumps(d,indent=2)+'\n');temporary.replace(a.output.with_suffix('.json'))
        a.output.with_suffix('.md').write_text('# Native-positive coverage qualification\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('rows','source_reports')},indent=2)+'\n```\n');print(json.dumps(d['gate']))


if __name__=='__main__':main()
