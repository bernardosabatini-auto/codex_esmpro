"""Validate all target shards of the alternating inference comparison."""
import argparse
import hashlib
import json
from pathlib import Path

from latentfold.metrics import paired_comparison
from matched_online_analysis import timing_result, selected_rows, VARIANTS
from summarize_comparison import validate_scores, means_by_target, hardware
from summarize_pilot import geometry_by_target


def analyze(runs):
    result = dict(status='incomplete', shards=[], failures=[], numerical_failures=[], independent_test_scored=False)
    combined = {n:[] for n in VARIANTS}
    chosen = {n:[] for n in VARIANTS}
    seen = set()
    signature = None
    shard_ids = set()
    scorer = None
    for run in runs:
        try:
            m = json.loads((run/'manifest.json').read_text())
            if m['status']!='complete':
                for name in VARIANTS:
                    child_path=run/name/'manifest.json'
                    if child_path.exists():
                        child=json.loads(child_path.read_text())
                        for control in child.get('controls',[]):
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99 or control['reference_ca_lddt_absolute_change']>.005:
                                result['numerical_failures'].append(dict(run=str(run),variant=name,**control))
                raise ValueError(m.get('error','incomplete collection'))
            c = m['config']
            for key in ('target_manifest','development_clusters','protocol'):
                if hashlib.sha256(Path(c[key]).read_bytes()).hexdigest()!=c[key+'_sha256']:
                    raise ValueError('changed '+key)
            sig = [m[k] for k in ('dataset','checkpoint','decoder_checkpoint','embedding_artifacts','timing_scope','variants')]+[c[k] for k in ('seed','all_target_ids','batches','protocol_sha256','development_clusters_sha256')]
            if signature is not None and sig!=signature:
                raise ValueError('shard provenance differs')
            signature = sig
            ids = set(c['target_ids'])
            if seen&ids or c['shard'] in shard_ids:
                raise ValueError('duplicate shard/target')
            timing = timing_result(m)
            shard = dict(run=str(run), shard=c['shard'], targets=len(ids),
                setup_and_controls_seconds=m['setup_and_controls_seconds'],
                elapsed_seconds=m['elapsed_seconds'],
                dual_resident_parameters=m['dual_resident_parameters'],
                active_pipeline_parameters=m['active_pipeline_parameters'], **timing)
            for name,v in VARIANTS.items():
                child = json.loads((run/name/'manifest.json').read_text())
                scores = json.loads((run/name/'scores.json').read_text())
                selection = json.loads((run/name/'choices.json').read_text())
                validate_scores(child,scores)
                if scorer is not None and scores['usalign']!=scorer:
                    raise ValueError('native scorer changed')
                scorer = scores['usalign']
                if child['config']['target_ids']!=c['target_ids'] or child['config']['flow_steps']!=[v['steps']] or child['precision']!=dict(embedding=v['embedding'],head=v['head'],decoder='fp32'):
                    raise ValueError('variant settings differ')
                controls = child['controls']
                if len(controls)!=8 or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 or r['reference_ca_lddt_absolute_change']>.005 for r in controls):
                    raise ValueError('numerical controls missing or failed')
                first = next(p for p in m['passes'] if p['variant']==name and p['repeat']==0)
                if selection['protocol_sha256']!=c['protocol_sha256'] or selection['choices']!=first['choices'] or selection['fingerprints']!=first['fingerprints']:
                    raise ValueError('frozen selection differs from timed first pass')
                combined[name].extend(scores['records'])
                chosen[name].extend(selected_rows(scores['records'],selection['choices']))
            try:
                shard['hardware'] = hardware(Path(str(run)+'_nsight.sqlite'),[b for p in m['passes'] for b in p['batches']])
            except Exception as error:
                shard['hardware'] = dict(status='unavailable',error=str(error))
            seen.update(ids)
            shard_ids.add(c['shard'])
            result['shards'].append(shard)
        except Exception as error:
            result['failures'].append(dict(run=str(run),error=f'{type(error).__name__}: {error}'))
    if result['failures']:
        if result['numerical_failures']:
            result.update(status='rejected_numerical_controls',development_gate_passed=False)
        return result
    if shard_ids!={0,1,2,3} or len(seen)!=626 or seen!=set(c['all_target_ids']):
        result['failures'].append(dict(error='Incomplete four-shard 626-target coverage'))
        return result
    clusters = json.loads(Path(c['development_clusters']).read_text())['clusters']
    if set(clusters)!=seen:
        raise ValueError('cluster map coverage differs')
    result['selected_structure_delta'] = {metric:paired_comparison(
        {r['target_id']:r[metric] for r in chosen['reference']},
        {r['target_id']:r[metric] for r in chosen['candidate']},clusters=clusters)
        for metric in ('tm_fixed_reference','ca_lddt')}
    result['three_sample_mean_delta'] = {metric:paired_comparison(
        means_by_target(combined['reference'],'steps25_cfg2',metric),
        means_by_target(combined['candidate'],'steps20_cfg2',metric),clusters=clusters)
        for metric in ('tm_fixed_reference','ca_lddt')}
    result['selected_geometry_delta'] = {field:paired_comparison(
        geometry_by_target(chosen['reference'],field),geometry_by_target(chosen['candidate'],field),clusters=clusters)
        for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
    result['aggregate_repeats'] = []
    for i in range(3):
        seconds = {n:sum(s['repeats'][i][n]['seconds'] for s in result['shards']) for n in VARIANTS}
        result['aggregate_repeats'].append(dict(seconds=seconds,speedup=seconds['reference']/seconds['candidate'],proteins_per_gpu_second={n:626/t for n,t in seconds.items()}))
    result['accuracy_gate_passed'] = all(v['ci95'][0]>=-.005 for v in result['selected_structure_delta'].values()) and all(v['ci95'][1]<=.001 for v in result['selected_geometry_delta'].values())
    result['speed_gate_passed'] = all(s['speed_gate_passed'] for s in result['shards']) and all(r['speedup']>=2 for r in result['aggregate_repeats'])
    result['development_gate_passed'] = result['accuracy_gate_passed'] and result['speed_gate_passed']
    result['status'] = 'complete'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,nargs='+',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = analyze(args.runs)
    args.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines = ['# Alternating sequence-to-selected-backbone comparison','',f"Status: {result['status']}.",'',
        'The planned comparison assigns 626 development proteins across four deterministic shards, with three alternating repeats of both pipelines on each GPU. Planned timings include CPU sample selection. Repeats are not extra targets or independent inference noise. Dual ESMC residency increases memory above standalone deployment. Numerical controls must pass before timing begins.']
    if result['status']=='complete':
        lines += ['', '| Repeat | Reference GPU seconds | Candidate GPU seconds | Speedup |','|---:|---:|---:|---:|']
        for i,r in enumerate(result['aggregate_repeats']):
            lines.append(f"| {i+1} | {r['seconds']['reference']:.2f} | {r['seconds']['candidate']:.2f} | {r['speedup']:.3f}x |")
        lines += ['', '| Selected metric | Reference | Candidate | Change | 95% cluster CI |','|---|---:|---:|---:|---|']
        for metric,r in result['selected_structure_delta'].items():
            lines.append(f"| {metric} | {r['ours']:.6f} | {r['theirs']:.6f} | {r['theirs_minus_ours']:+.6f} | {r['ci95']} |")
        lines += ['', f"Accuracy gate: {result['accuracy_gate_passed']}. Speed gate (every shard/repeat >=2x and identical repeat outputs): {result['speed_gate_passed']}."]
        lines += ['', '| Shard | Setup + controls (s) | Process elapsed (s) | Collection SM issue | Whole capture SM issue |',
            '|---:|---:|---:|---:|---:|']
        for shard in result['shards']:
            counters=shard['hardware']
            issue=counters.get('collection_mean_percent',{}).get('SM Issue [Throughput %]')
            whole=counters.get('whole_capture_mean_percent',{}).get('SM Issue [Throughput %]')
            issue_text=f'{issue:.1f}%' if issue is not None else 'unavailable'
            whole_text=f'{whole:.1f}%' if whole is not None else 'unavailable'
            lines.append(f"| {shard['shard']} | {shard['setup_and_controls_seconds']:.1f} | {shard['elapsed_seconds']:.1f} | {issue_text} | {whole_text} |")
        lines += ['', 'SM instruction issue is a measured hardware counter, not percent of peak FLOPs. Whole capture includes setup and controls, but excludes profiler export.',
            '', '| Selected geometry fraction | Candidate minus reference | 95% cluster CI |', '|---|---:|---|']
        for field,row in result['selected_geometry_delta'].items():
            lines.append(f"| {field} | {row['theirs_minus_ours']:+.6f} | {row['ci95']} |")
    else:
        lines += ['', *[str(r) for r in result['failures']]]
        if result['numerical_failures']:
            lines += ['', '| Task | Variant | Length bucket | CA RMSD (A) | Cross-prediction CA lDDT | Native CA lDDT absolute change |',
                '|---|---|---:|---:|---:|---:|']
            for row in result['numerical_failures']:
                lines.append(f"| {Path(row['run']).name} | {row['variant']} | {row['bucket']} | {row['ca_rmsd']:.6f} | {row['ca_lddt']:.6f} | {row['reference_ca_lddt_absolute_change']:.6f} |")
            lines += ['', 'Required bounds: RMSD <=0.2 A, cross-prediction CA lDDT >=0.99, native CA lDDT absolute change <=0.005. The candidate is rejected under these unchanged bounds. No repeated throughput or selected-accuracy result is available.']
    lines += ['', 'The 34 independent-test structures remain unscored. No optimized ESMFold2 throughput comparison is claimed.']
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    main()
