"""Audit oracle teacher positives under the unchanged same-valid-refold assay."""
import argparse,fcntl,json
from pathlib import Path


def ready_command(root):
    path=root/'runs/fragment_repaint_teacher_comparison.json';output=root/'reports/fragment_repaint_teacher_comparison_20261003'
    if not path.exists() or output.with_suffix('.json').exists():return None
    plan=json.loads(path.read_text());ids=plan['jobs']
    if not plan.get('oracle_teacher_comparison') or len(ids)!=4:raise ValueError('Invalid teacher comparison plan')
    if any(i is None for i in ids):return None
    own={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if len(set(ids))!=4 or any(i not in own or own[i]['completion_action']!='summarize_fragment_preference_refold' for i in ids):raise ValueError('Unregistered or duplicated teacher refolds')
    if not all((root/f'reports/fragment_preference_refold_{i}.json').exists() and json.loads((root/f'reports/fragment_preference_refold_{i}.json').read_text())['status']=='complete' for i in ids):return None
    return [str(root/'scripts/compare_fragment_repaint_teacher.py'),'--plan',str(path),'--output',str(output)]


def teacher_gate(summary):
    return summary['strong']>8 and summary['strong_families']>=7 and summary['designable']>=45


def compare(plan,root):
    from prepare_overfit import sha
    import numpy as np
    from prepare_fragment_preference_refold import audit_inputs,TEACHER_KEYS
    from compare_native_anchor_models import verify_outcome,diversity
    from compare_extra_fragment_refolds import clustered
    baseline=root/'reports/fragment_preference_comparison_20261003.json'
    if sha(baseline)!=plan['baseline_comparison_sha256']:raise ValueError('Changed reused comparison')
    prior=json.loads(baseline.read_text())
    for source in prior['sources']:
        if sha(source['report'])!=source['report_sha256']:raise ValueError('Changed parent refolds')
    paths={'parent6000':[Path(r['report']) for r in prior['sources']], 'oracle_repaint':[root/f'reports/fragment_preference_refold_{i}.json' for i in plan['jobs']]}
    configs={};generations={};arms={};sources=[]
    for arm,paths0 in paths.items():
        rows=[];parts=set();cached=None;generation_hash=None
        for rp in paths0:
            run=root/'runs'/rp.stem;mp=run/'manifest.json';m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];gc,spec=audit_inputs(c,audited_generation=cached);cached=(gc,spec)
            if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or d['refolded_sha256']!=sha(run/'refolded.h5')
                    or d['completed_refolds']!=256 or len(d['records'])!=32 or c['partition'] in parts or d['partition']!=c['partition']
                    or d['generation_manifest_sha256']!=c['generation_manifest_sha256'] or not m['teacher_deterministic_algorithms'] or gc['arm']!=arm):raise ValueError('Incomplete teacher refold partition')
            if generation_hash is not None and generation_hash!=c['generation_manifest_sha256']:raise ValueError('Mixed generations')
            generation_hash=c['generation_manifest_sha256'];parts.add(c['partition'])
            if [r['name'] for r in d['records']]!=[r['name'] for r in c['entries']]:raise ValueError('Changed record order')
            for r in d['records']:
                if r['arm']!=arm or len(r['refolds'])!=8:raise ValueError('Changed sequence budget')
                verify_outcome(r)
            rows.extend(d['records']);sources.append(dict(path=str(rp),sha256=sha(rp)));configs[arm,c['partition']]=c
            generations[arm]=dict(generation_manifest=c['generation_manifest'],config=gc)
        wanted={(r['id'],k) for r in gc['selected'] for k in range(4)}
        if parts!=set(range(4)) or len(rows)!=128 or {(r['target_id'],r['generation_slot']) for r in rows}!=wanted:raise ValueError('Changed128-output denominator')
        arms[arm]=rows
    base=generations['parent6000']['config'];gc=generations['oracle_repaint']['config']
    if (gc.get('oracle_teacher_refold') is not True or gc['selected']!=base['selected'] or gc['native_sources']!=base['native_sources']
            or sha(generations['oracle_repaint']['generation_manifest'])!=plan['generation_manifest_sha256']):raise ValueError('Changed declared teacher generation')
    for part in range(4):
        a,b=configs['oracle_repaint',part],configs['parent6000',part]
        if any(a[k]!=b[k] for k in TEACHER_KEYS):raise ValueError('Unmatched design/refolding recipe')
        fields=('target_id','family','length','generation_slot','fixed_start','fixed_sequence','repeatability_control')
        if any(x[k]!=y[k] for x,y in zip(a['entries'],b['entries']) for k in fields):raise ValueError('Unmatched supplied constraints')
    summary=[];contrasts=[]
    for bucket in (None,128,256,384,512):
        subsets={a:[r for r in rows if bucket is None or r['bucket']==bucket] for a,rows in arms.items()}
        for arm,rows in subsets.items():
            summary.append(dict(arm=arm,bucket=bucket,samples=len(rows),raw=sum(r['raw_gate_passed'] for r in rows),strong=sum(r['scaffold_joint_success'] for r in rows),designable=sum(r['valid_designable'] for r in rows),strong_families=len({r['family'] for r in rows if r['scaffold_joint_success']})))
        families=sorted({r['family'] for r in subsets['parent6000']})
        contrasts.append(dict(bucket=bucket,metrics={metric:clustered([np.mean([r[metric] for r in subsets['oracle_repaint'] if r['family']==f])-np.mean([r[metric] for r in subsets['parent6000'] if r['family']==f]) for f in families]) for metric in ('raw_gate_passed','scaffold_joint_success','valid_designable')}))
    totals={r['arm']:r for r in summary if r['bucket'] is None}
    if tuple(totals['parent6000'][k] for k in ('strong','strong_families','designable'))!=(8,7,45):raise ValueError('Parent outcomes changed')
    passing={a:{(r['target_id'],r['generation_slot']) for r in rows if r['scaffold_joint_success']} for a,rows in arms.items()}
    overlap=dict(shared=len(passing['parent6000']&passing['oracle_repaint']),teacher_only=len(passing['oracle_repaint']-passing['parent6000']),parent_only=len(passing['parent6000']-passing['oracle_repaint']))
    dr=diversity(generations['oracle_repaint'],arms['oracle_repaint'],configs['oracle_repaint',0]['usalign'])
    return dict(status='complete',oracle_teacher=True,source_reports=sources,summary=summary,contrasts=contrasts,teacher_label_pilot_qualified=teacher_gate(totals['oracle_repaint']),overlap=overlap,teacher_diversity=dr,native=prior['native'],new_refolds=1024,reused_parent_refolds=1024,scope='Repeated32training-protein oracle-label feasibility. Native-context motif codes are teacher-only information. Same valid refold must retain motif and agree globally and on scaffold. No student improvement, generalization or experimental claim.')


def main():
    from prepare_overfit import sha
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    with a.output.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);plan=json.loads(a.plan.read_text());d=compare(plan,root);d['plan_sha256']=sha(a.plan)
        temp=a.output.with_suffix('.tmp');temp.write_text(json.dumps(d,indent=2)+'\n');temp.replace(a.output.with_suffix('.json'))
        lines=['# Oracle RePaint teacher: same-refold feasibility','','All128 outputs and1024 designs retained. Teacher uses native-context motif codes; this is not isolated-fragment inference.','', '| Arm | Raw | Strict | Designable | Successful families |','|---|---:|---:|---:|---:|']
        for r in d['summary']:
            if r['bucket'] is None:lines.append(f"|{r['arm']}|{r['raw']}|{r['strong']}|{r['designable']}|{r['strong_families']}|")
        lines+=['',f"Teacher-label pilot qualified: {d['teacher_label_pilot_qualified']}. Overlap: {d['overlap']}. Strict teacher-minus-parent contrast: {d['contrasts'][0]['metrics']['scaffold_joint_success']}.",'',d['scope']]
        a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(d['summary'][:2]))


if __name__=='__main__':main()
