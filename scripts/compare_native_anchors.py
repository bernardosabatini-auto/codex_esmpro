"""Independent native-anchor qualification, without rescuing prior failed gates."""
import json
from pathlib import Path
from native_anchor_calibration import native_pair
from prepare_fragment_preference_refold import audit_inputs
from prepare_overfit import sha
from compare_fragment_preferences import feasibility_gate


def native_gate(preferences,selected,native_passes,limits):
    gate=feasibility_gate(preferences,selected,native_passes,limits)
    gate['checks']['native_both_strict']=sum(r['native_both_strict'] for r in preferences)>=limits['minimum_native_both_strict']
    gate['qualified']=all(gate['checks'].values())
    return gate


def compare_native(runs,root):
    records=[];preferences=[];parts=set();sources=[];gc=None;spec=None;generation_hash=None
    for run in runs:
        run=run.resolve();mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json')
        m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];this_gc,this_spec=audit_inputs(c)
        if gc is None:gc=this_gc;spec=this_spec;generation_hash=c['generation_manifest_sha256']
        if (not spec.get('native_anchor_calibration') or this_gc!=gc or this_spec!=spec
                or m['status']!='complete' or d['status']!='complete' or not d['native_anchor_calibration']
                or d['manifest_sha256']!=sha(mp) or d['refolded_sha256']!=sha(run/'refolded.h5')
                or d['completed_refolds']!=192 or d['generation_manifest_sha256']!=generation_hash
                or c['partition'] in parts or c['partition']!=d['partition']
                or not m['teacher_deterministic_algorithms']):raise ValueError('Incomplete or mismatched anchor partitions')
        if len(d['records'])!=24 or [r['name'] for r in d['records']]!=[r['name'] for r in c['entries']]:raise ValueError('Changed anchor inventory')
        parts.add(c['partition']);records.extend(d['records']);preferences.extend(d['preferences'])
        sources.append(dict(manifest=str(mp),manifest_sha256=sha(mp),report=str(rp),report_sha256=sha(rp)))
    wanted={(arm,r['id'],k) for r in gc['selected'] for arm,count in [('parent6000',4),('native_latent',2)] for k in range(count)}
    if (parts!=set(range(4)) or len(records)!=96 or len(preferences)!=16
            or {(r['arm'],r['target_id'],r['generation_slot']) for r in records}!=wanted):raise ValueError('Changed full96-backbone denominator')
    params={k:spec['preference'][k] for k in ('minimum_quality','discovery_margin','confirmation_margin')}
    recomputed=[native_pair(sorted([r for r in records if r['target_id']==ident and r['arm']=='native_latent'],key=lambda r:r['generation_slot']),
                            [r for r in records if r['target_id']==ident and r['arm']=='parent6000'],**params) for ident in gc['target_ids']]
    if json.loads(json.dumps(recomputed))!=sorted(preferences,key=lambda r:r['target_id']):raise ValueError('Changed native preference selection')
    native=[]
    for row in gc['selected']:
        report=json.loads(Path(row['native_report']).read_text());r=next(x for x in report['records'] if x['name']==row['native_name'])
        if len(r['refolds'])!=8 or len(r['scaffold_scores'])!=8:raise ValueError('Native budget changed')
        passed=bool(r['raw']['coarse_valid'] and any(x['coarse_valid'] and x['sc_tm']>.5 and r['scaffold_scores'][k]>.5 for k,x in enumerate(r['refolds'])))
        native.append(dict(target_id=row['id'],global_scaffold=passed,strong=r['scaffold_joint_success']))
    gate=native_gate(recomputed,gc['selected'],sum(r['global_scaffold'] for r in native),spec['preference'])
    summary=[]
    for arm in ('parent6000','native_latent'):
        rows=[r for r in records if r['arm']==arm]
        summary.append(dict(arm=arm,samples=len(rows),raw_matches=sum(r['raw_gate_passed'] for r in rows),
                            strong=sum(r['scaffold_joint_success'] for r in rows),designable=sum(r['valid_designable'] for r in rows)))
    return dict(status='complete',training_only=True,sources=sources,protocol=gc['protocol'],protocol_sha256=sha(gc['protocol']),
                generation_manifest_sha256=generation_hash,generated=64,native_decodes=32,refolds=768,
                native_budgets_reused=16,native_global_scaffold=sum(r['global_scaffold'] for r in native),
                summary=summary,native_both_strict=sum(r['native_both_strict'] for r in recomputed),gate=gate,preferences=recomputed,native=native,
                decision='Preregister positive-only versus bounded reference-anchored contrastive training.' if gate['qualified'] else 'Close native-anchor qualification; no training, threshold sweep, source substitution or added attempts.',
                scope='Disjoint training-only native-latent qualification. Both native decoder realizations must separately satisfy strict same-refold criteria and full-native roundtrip<=1A. Native attempts are never pooled. Previous generated-only gate remains failed. No generalization claim.')
