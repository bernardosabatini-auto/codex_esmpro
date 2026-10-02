"""Compare the declared short-sampler pipeline to both frozen25-step controls."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from compare_retry_ensembles import comparisons,gates,validate_source
from summarize_bounded_retry_native import analyze as native_analysis
from retry_sampler_settings import external_steps


def matched_settings(candidate,reference,recipe):
    for c in (candidate,reference):
        external_steps(c,recipe)
        if c.get('latent_noise_scheme','iid')!='iid':raise ValueError('Non-IID sampler')
    keys=('samples','max_attempts','noise_arms','seed','flow_solver','flow_time_power','panel_sha256','embedding_cache_sha256','decoder_checkpoint_sha256')
    if any(candidate[k]!=reference[k] for k in keys):raise ValueError('Unmatched external settings')
    expected={'original':(2,False),'compact500':(1,True),'reflow10':(1,False)}
    for c in (candidate,reference):
        if (c['primary_guidance'],c['compact_condition'])!=expected[c['name']]:raise ValueError('Undeclared guidance/conditioning')


def analyze(run,scores,protocol):
    recipe=json.loads(protocol.read_text());native_path=Path(recipe['native_run'])/'manifest.json';native=json.loads(native_path.read_text());qualification=native_analysis(native)
    if not all(r['quality_passed'] for r in qualification['summaries'].values()):raise ValueError('Native quality failed')
    sources={name:(Path(r['run']),Path(r['scores'])) for name,r in recipe['reused_controls'].items()};sources['reflow10']=(run,scores);arms={};definitions=None;candidate=json.loads((run/'manifest.json').read_text())['config']
    if set(sources)!=set(recipe['heads']):raise ValueError('Missing declared heads')
    for name,(directory,scorepath) in sources.items():
        m=json.loads((directory/'manifest.json').read_text());c=m['config'];score=json.loads(scorepath.read_text());audit=json.loads((Path('reports')/(directory.name+'.json')).read_text())
        if c['name']!=name or m['status']!='complete' or score['status']!='complete' or audit['status']!='complete' or audit['manifest_sha256']!=sha(directory/'manifest.json') or audit['predictions_sha256']!=sha(directory/'predictions.h5'):raise ValueError('Incomplete or changed artifacts')
        validate_source(directory,c,protocol,recipe,native);matched_settings(candidate,c,recipe)
        if sha(c['native_manifest'])!=c['native_manifest_sha256'] or score['run']!=str(directory.resolve()) or score['protocol_sha256']!=sha('configs/ensemble_scoring_protocol.json'):raise ValueError('Wrong native/scoring evidence')
        if name in recipe['reused_controls'] and sha(scorepath)!=recipe['reused_controls'][name]['scores_sha256']:raise ValueError('Reused scores changed')
        if definitions is None:definitions=score['definitions']
        if score['definitions']!=definitions:raise ValueError('Changed state definitions')
        rows={mode:{r['target_id']:r for r in score['rows'] if r['setting']==f"cfg{c['primary_guidance']}/{mode}"} for mode in ('raw','latent')}
        if len(score['rows'])!=96 or any(len(r)!=48 for r in rows.values()):raise ValueError('Missing raw/selected rows')
        arms[name]=dict(rows=rows,cost=audit,score_sha256=sha(scorepath))
    metrics={name:{mode:comparisons(arms['reflow10']['rows'][mode],arms[name]['rows'][mode]) for mode in ('raw','latent')} for name in ('original','compact500')}
    return dict(status='complete',protocol_sha256=sha(protocol),metrics=metrics,sampling_quality_gate_passed=gates(metrics['original']['latent'])['sampling_quality'],compact_quality_noninferior=gates(metrics['compact500']['latent'])['sampling_quality'],retry_effect=comparisons(arms['reflow10']['rows']['latent'],arms['reflow10']['rows']['raw']),costs={name:r['cost'] for name,r in arms.items()},scores_sha256={name:r['score_sha256'] for name,r in arms.items()})


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--scores',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/reflow_retry_ensemble_protocol.json'));a=p.parse_args();d=analyze(a.run,a.scores,a.protocol);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Archived10-step bounded-retry external comparison','','All48 development families,16 state-eligible families, unchanged thresholds and all failures retained. Frozen original and compact25-step controls reused through exact native/source lineage. New10-step candidate uses expanded conditioning; compact500 uses compact conditioning.','','| Reference | Selected metric | Reflow10 | Reference | Difference |95% family interval |','|---|---|---:|---:|---:|---|']
    for name,modes in d['metrics'].items():
        for key,r in modes['latent'].items():lines.append(f"| {name} | {key} | {r['candidate']:.5f} | {r['reference']:.5f} | {r['candidate_minus_reference']:+.5f} | {r['ci95']} |")
    lines+=['',f"External quality versus original:{d['sampling_quality_gate_passed']}; versus compact500:{d['compact_quality_noninferior']}."]
    for name,c in d['costs'].items():lines+=['',f"{name}: recovered{c['recovered']}/{c['initially_invalid']}, exhausted{c['exhausted']}; attempts/output{c['attempts_per_output']:.5f}; generation{c['initial_seconds']:.2f}s + retries{c['retry_seconds']:.2f}s; peak{c['peak_reserved_gib']:.2f}GiB."]
    lines+=['','MD W1 is better when lower and always reported. Cached-conditioner generation timings exclude ESM, geometry checks, loading and I/O: no end-to-end speed claim. Passing original does not imply equivalence to compact. Raw native failure remains unchanged. No equilibrium, independent-test or new-diversity claim; locked tests unscored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
