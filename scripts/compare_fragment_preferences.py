"""Prospective split-confirmation gate; strict scaffolding remains unchanged."""
import argparse
import json
from pathlib import Path



def ready_command(root):
    """Fixed CPU completion comparison; never submits GPU work."""
    for plan_name, output_name in [('fragment_preference_comparison','fragment_preference_comparison_20261003'),
                                   ('native_anchor_comparison','native_anchor_comparison_20261003')]:
        path=root/'runs'/(plan_name+'.json')
        if not path.exists():continue
        plan=json.loads(path.read_text());ids=plan['jobs']
        if len(ids)!=4 or len(set(ids))!=4:raise ValueError('Expected four declared partitions')
        registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
        if any(i not in registry or registry[i].get('completion_action')!='summarize_fragment_preference_refold' for i in ids):
            raise ValueError('Unregistered preference comparison job')
        reports=[root/f'reports/fragment_preference_refold_{i}.json' for i in ids]
        if not all(p.exists() for p in reports):continue
        data=[json.loads(p.read_text()) for p in reports]
        if any(d['status']!='complete' for d in data):continue
        if any(d['generation_manifest_sha256']!=plan['generation_manifest_sha256'] for d in data):
            raise ValueError('Changed comparison generation')
        output=root/'reports'/output_name
        if output.with_suffix('.json').exists():continue
        return [str(root/'scripts/compare_fragment_preferences.py'),'--runs',
                *[str(root/f'runs/fragment_preference_refold_{i}') for i in ids],'--output',str(output)]
    from compare_native_anchor_models import ready_command as ready_models
    from compare_native_positive_coverage import ready_command as ready_positives
    return ready_models(root) or ready_positives(root)


def feasibility_gate(preferences, selected, native_passes, limits):
    eligible=sum(r['eligible'] for r in preferences)
    confirmed=[r for r in preferences if r['confirmed']]
    metadata={r['id']:r for r in selected}
    buckets={metadata[r['target_id']]['bucket'] for r in confirmed}
    rate=len(confirmed)/eligible if eligible else 0.
    checks=dict(coverage=len(confirmed)>=limits['minimum_confirmed'],
                confirmation_rate=rate>=limits['minimum_confirmation_rate'],
                length_buckets=len(buckets)>=limits['minimum_buckets'],
                long_proteins=sum(metadata[r['target_id']]['length']>256 for r in confirmed)>=limits['minimum_long_confirmed'],
                native_calibration=native_passes>=limits['minimum_native_global_scaffold'])
    return dict(qualified=all(checks.values()),checks=checks,eligible=eligible,confirmed=len(confirmed),confirmation_rate=rate)


def compare(runs,root):
    first=json.loads((runs[0]/'manifest.json').read_text())
    generation=json.loads(Path(first['config']['generation_manifest']).read_text())
    if generation['config']['spec'].get('native_anchor_calibration'):
        from compare_native_anchors import compare_native
        return compare_native(runs,root)
    from latentfold.fragment_preferences import split_preference
    from prepare_fragment_preference_refold import audit_inputs
    from prepare_overfit import sha
    records=[];preferences=[];parts=set();sources=[];generation_hash=None;gc=None;spec=None
    for run in runs:
        run=run.resolve();mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json')
        m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];this_gc,this_spec=audit_inputs(c)
        if generation_hash is None:generation_hash=c['generation_manifest_sha256'];gc=this_gc;spec=this_spec
        if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp)
                or d['refolded_sha256']!=sha(run/'refolded.h5') or d['completed_refolds']!=256
                or d['generation_manifest_sha256']!=generation_hash or this_gc!=gc or this_spec!=spec
                or d['partition']!=c['partition'] or c['partition'] in parts
                or not m['teacher_deterministic_algorithms']):raise ValueError('Incomplete or mismatched partitions')
        if len(d['records'])!=32 or [r['name'] for r in d['records']]!=[r['name'] for r in c['entries']]:raise ValueError('Wrong scored inventory')
        parts.add(c['partition']);records.extend(d['records']);preferences.extend(d['preferences'])
        sources.append(dict(manifest=str(mp),manifest_sha256=sha(mp),report=str(rp),report_sha256=sha(rp)))
    if parts!=set(range(4)) or len(records)!=128 or len(preferences)!=32:raise ValueError('Incomplete fixed study')
    wanted={(r['id'],k) for r in gc['selected'] for k in range(4)}
    if {(r['target_id'],r['generation_slot']) for r in records}!=wanted:raise ValueError('Changed full denominator')
    params={k:spec['preference'][k] for k in ('minimum_quality','discovery_margin','confirmation_margin')}
    recomputed=[split_preference([dict(r,slot=r['generation_slot']) for r in records if r['target_id']==ident],**params) for ident in gc['target_ids']]
    # JSON object keys become strings; normalize solely for exact comparison.
    if json.loads(json.dumps(sorted(recomputed,key=lambda r:r['target_id'])))!=sorted(preferences,key=lambda r:r['target_id']):raise ValueError('Preference selection changed')
    native=[]
    for row in gc['selected']:
        report=json.loads(Path(row['native_report']).read_text())
        r=next(x for x in report['records'] if x['name']==row['native_name'])
        if len(r['refolds'])!=8 or len(r['scaffold_scores'])!=8:raise ValueError('Native budget changed')
        passed=bool(r['raw']['coarse_valid'] and any(x['coarse_valid'] and x['sc_tm']>.5 and r['scaffold_scores'][k]>.5 for k,x in enumerate(r['refolds'])))
        native.append(dict(target_id=row['id'],global_scaffold=passed,strong=r['scaffold_joint_success']))
    gate=feasibility_gate(recomputed,gc['selected'],sum(r['global_scaffold'] for r in native),spec['preference'])
    return dict(status='complete',training_only=True,sources=sources,protocol=gc['protocol'],protocol_sha256=sha(gc['protocol']),
                generated=128,refolds=1024,native_budgets_reused=32,native_global_scaffold=sum(r['global_scaffold'] for r in native),
                raw_matches=sum(r['raw_gate_passed'] for r in records),strong=sum(r['scaffold_joint_success'] for r in records),
                strong_families=len({r['family'] for r in records if r['scaffold_joint_success']}),
                designable=sum(r['valid_designable'] for r in records),gate=gate,preferences=recomputed,native=native,
                by_length=[dict(bucket=b,generated=sum(r['bucket']==b for r in records),strong=sum(r['bucket']==b and r['scaffold_joint_success'] for r in records),designable=sum(r['bucket']==b and r['valid_designable'] for r in records)) for b in (128,256,384,512)],
                decision='Preregister bounded preference-training pilot; no generalization claim.' if gate['qualified'] else 'Close this collection recipe; do not train on unqualified preferences or increase attempts/cutoff sweeps.',
                scope='Training-only label-feasibility collection, not model improvement. Strict1A success and graded2A preference feasibility are distinct. All128outputs retained; global/scaffold/motif evidence must share a valid refold.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=4,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=compare(a.runs,Path(__file__).resolve().parents[1]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    view={k:v for k,v in d.items() if k not in ('sources','preferences','native')}
    a.output.with_suffix('.md').write_text('# Training-only preference calibration\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')
    print(json.dumps(view))


if __name__=='__main__':main()
