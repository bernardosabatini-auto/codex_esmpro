"""Matched raw and retry outcomes for all declared external pipelines."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from compare_ensemble_scores import compare
from summarize_bounded_retry_native import analyze as analyze_native


def values(rows,key):
    getters=dict(coverage_at_32=lambda r:r['coverage']['2.0']['32'],both_states=lambda r:float(r['coverage']['2.0']['32']==1.),ca_lddt=lambda r:r['oracle_nearest_reference_ca_lddt_mean'],coarse_valid=lambda r:r['coarse_valid_fraction'],md_w1=lambda r:r['projection_wasserstein']['32'])
    result={}
    for ident,r in rows.items():
        try:result[ident]=getters[key](r)
        except KeyError:continue
    return result


def comparisons(candidate,reference):
    if set(candidate)!=set(reference) or len(candidate)!=48 or any((candidate[i]['family'],candidate[i]['category'])!=(reference[i]['family'],reference[i]['category']) for i in candidate):raise ValueError('Unmatched families/categories')
    families={i:r['family'] for i,r in candidate.items()}
    metrics={k:compare(values(candidate,k),values(reference,k),families) for k in ('coverage_at_32','both_states','ca_lddt','coarse_valid','md_w1')}
    if metrics['coverage_at_32']['families']!=16 or metrics['coarse_valid']['families']!=48:raise ValueError('Coverage/validity scope changed')
    return metrics


def gates(metrics):
    accuracy=metrics['ca_lddt']['ci95'][0]>-.005;validity=metrics['coarse_valid']['candidate_minus_reference']>=-.01;coverage=metrics['coverage_at_32']
    return dict(sampling_quality=bool(accuracy and validity and coverage['candidate_minus_reference']>=0),training_diversity=bool(accuracy and validity and coverage['candidate_minus_reference']>=.1 and coverage['ci95'][0]>0))


def validate_source(run,c,recipe,protocol,native):
    reused=protocol.get('reused_controls',{}).get(c['name'])
    if reused:
        if run.resolve()!=Path(reused['run']).resolve() or sha(run/'manifest.json')!=reused['manifest_sha256'] or sha(protocol['reuse_protocol'])!=protocol['reuse_protocol_sha256'] or c['protocol_sha256']!=protocol['reuse_protocol_sha256'] or c['native_manifest_sha256']!=native['config'].get('prior_retry_manifest_sha256'):
            raise ValueError('Unproven original control reuse')
    elif c['protocol_sha256']!=sha(recipe) or c['native_manifest_sha256']!=sha(Path(protocol['native_run'])/'manifest.json'):
        raise ValueError('Wrong source recipe/native lineage')
    head=next(h for h in native['config']['heads'] if h['name']==c['name'])
    if (c['checkpoint'],c['checkpoint_sha256'],c['primary_guidance'])!=(head['checkpoint'],head['checkpoint_sha256'],head['guidance']):raise ValueError('Wrong qualified checkpoint')


def analyze(runs,scores,recipe=Path('configs/retry_ensemble_protocol.json')):
    recipe=Path(recipe);protocol=json.loads(recipe.read_text());arms={};definitions=None;shared=None
    if len(runs)!=len(protocol['heads']) or len(scores)!=len(runs):raise ValueError('All declared heads required')
    native_path=Path(protocol['native_run'])/'manifest.json';native=json.loads(native_path.read_text());qualification=analyze_native(native)
    if not all(r['quality_passed'] for r in qualification['summaries'].values()):raise ValueError('Native retry qualification failed')
    for run,scorepath in zip(runs,scores):
        path=run/'manifest.json';m=json.loads(path.read_text());c=m['config'];s=json.loads(scorepath.read_text());audit_path=Path('reports')/(run.name+'.json');audit=json.loads(audit_path.read_text());name=c['name']
        if name in arms or name not in protocol['heads'] or m['status']!='complete' or s['status']!='complete' or audit['status']!='complete' or audit['manifest_sha256']!=sha(path) or audit['predictions_sha256']!=sha(run/'predictions.h5'):raise ValueError('Missing/duplicate/changed source evidence')
        if s['run']!=str(run.resolve()) or s['protocol_sha256']!=sha('configs/ensemble_scoring_protocol.json') or sha(c['native_manifest'])!=c['native_manifest_sha256']:raise ValueError('Wrong source/scoring evidence')
        validate_source(run,c,recipe,protocol,native)
        settings={key:c[key] for key in ('samples','max_attempts','noise_arms','seed','flow_steps','flow_solver','flow_time_power','panel_sha256','embedding_cache_sha256','decoder_checkpoint_sha256')}
        if definitions is None:definitions=s['definitions'];shared=settings
        if s['definitions']!=definitions or settings!=shared:raise ValueError('Unmatched definitions or sampling settings')
        rows={mode:{r['target_id']:r for r in s['rows'] if r['setting']==f"cfg{c['primary_guidance']}/{mode}"} for mode in ('raw','latent')}
        if len(s['rows'])!=96 or any(len(r)!=48 for r in rows.values()):raise ValueError('Missing raw/selected scores')
        arms[name]=dict(rows=rows,audit=audit,run=str(run),score=str(scorepath),score_sha256=sha(scorepath))
    if set(arms)!=set(protocol['heads']):raise ValueError('Missing declared head')
    d=dict(status='complete',protocol_sha256=sha(recipe),arms={})
    for name,r in arms.items():
        versus={mode:comparisons(r['rows'][mode],arms['original']['rows'][mode]) for mode in ('raw','latent')}
        d['arms'][name]=dict(versus_original=versus,retry_effect=comparisons(r['rows']['latent'],r['rows']['raw']),selected_gates=gates(versus['latent']),cost=r['audit'],sources={k:r[k] for k in ('run','score','score_sha256')})
    broader_names=[n for n in protocol['heads'] if n.startswith('seed')]
    if len(broader_names)!=2 or not all(any(n.startswith(f'seed{seed}_') for n in broader_names) for seed in (2026100171,2026100181)):raise ValueError('Both declared broader seeds required')
    broader=[d['arms'][n]['selected_gates'] for n in broader_names]
    d['replicated_broader_sampling_quality']=all(r['sampling_quality'] for r in broader)
    d['replicated_broader_training_diversity']=all(r['training_diversity'] for r in broader)
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--scores',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path,default=Path('configs/retry_ensemble_protocol.json'));a=p.parse_args();d=analyze(a.runs,a.scores,a.protocol)
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Matched external bounded-retry results','','All48 frozen development families, including all16 eligible two-state families. Raw and selected32 scored separately using unchanged definitions; all failures retained. Selected candidates compare against selected original, with all declared heads included.','','| Pipeline | Selected CA-lDDT | Valid fraction | State coverage | Both-state fraction | MD W1 | Sampling quality | Training diversity |','|---|---:|---:|---:|---:|---:|---|---|']
    for name,r in d['arms'].items():
        v=r['versus_original']['latent'];g=r['selected_gates'];lines.append('| '+name+' | '+' | '.join(f"{v[k]['candidate']:.5f}" for k in ('ca_lddt','coarse_valid','coverage_at_32','both_states','md_w1'))+f" | {g['sampling_quality']} | {g['training_diversity']} |")
    for name,r in d['arms'].items():
        lines+=['',f'## {name}','']
        for mode in ('raw','latent'):
            for key,e in r['versus_original'][mode].items():lines.append(f"- {mode} minus matched original, {key}: {e['candidate_minus_reference']:+.5f}, paired-family95% interval {e['ci95']}.")
        effect=r['retry_effect'];cost=r['cost'];lines+=['',f"Selected-minus-raw coverage:{effect['coverage_at_32']['candidate_minus_reference']:+.5f}; validity:{effect['coarse_valid']['candidate_minus_reference']:+.5f}; CA-lDDT:{effect['ca_lddt']['candidate_minus_reference']:+.5f}; MD W1:{effect['md_w1']['candidate_minus_reference']:+.5f}.",f"Recovered{cost['recovered']}/{cost['initially_invalid']} initially invalid outputs; exhausted{cost['exhausted']}; attempts/output{cost['attempts_per_output']:.5f}. Generation{cost['initial_seconds']:.2f}s + retries{cost['retry_seconds']:.2f}s; peak{cost['peak_reserved_gib']:.2f}GiB."]
    lines+=['',f"Replicated broader sampling quality:{d['replicated_broader_sampling_quality']}; replicated broader training diversity:{d['replicated_broader_training_diversity']}.",'','MD W1 is better when lower and remains reported even when the formal quality gate passes. Generation timings exclude ESM, loading, controls, geometry selection and disk I/O; end-to-end timing is still required. Oracle CA-lDDT is nearest-reference quality per sample, never reference-based deployment selection. These are development results, not independent-test or equilibrium-population claims. Raw-model native failures remain unchanged.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
