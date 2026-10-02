"""Compare antithetic and IID sampling at identical qualified model weights."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from compare_retry_ensembles import comparisons,gates
from summarize_bounded_retry_native import analyze as native_analysis


def same_model(candidate,baseline):
    keys=('checkpoint_sha256','seed','primary_guidance','compact_condition','samples','max_attempts','flow_steps','flow_solver','flow_time_power','panel_sha256','embedding_cache_sha256','decoder_checkpoint_sha256')
    if any(candidate[k]!=baseline[k] for k in keys) or candidate.get('latent_noise_scheme')!='antithetic' or baseline.get('latent_noise_scheme','iid')!='iid':raise ValueError('Unmatched model or sampler controls')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--scores',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads((a.run/'manifest.json').read_text());c=m['config'];protocol=Path(c['protocol']);recipe=json.loads(protocol.read_text());basepath=Path(recipe['baseline_run'])/'manifest.json';base=json.loads(basepath.read_text());same_model(c,base['config'])
    if sha(protocol)!=c['protocol_sha256'] or c['name']!='compact500_antithetic' or base['config']['name']!='compact500' or sha(basepath)!=c['positive_parent_manifest_sha256']:raise ValueError('Changed identity evidence')
    native=Path(c['native_manifest'])
    if sha(native)!=c['native_manifest_sha256'] or not native_analysis(json.loads(native.read_text())).get('antithetic_qualified'):raise ValueError('Native antithetic noninferiority missing')
    audit=json.loads((Path('reports')/(a.run.name+'.json')).read_text())
    if m['status']!='complete' or base['status']!='complete' or audit['status']!='complete' or audit['manifest_sha256']!=sha(a.run/'manifest.json') or audit['predictions_sha256']!=sha(a.run/'predictions.h5'):raise ValueError('Incomplete/changed output audit')
    left=json.loads(a.scores.read_text());rightpath=Path(recipe['baseline_scores']);right=json.loads(rightpath.read_text())
    if sha(rightpath)!=c['positive_parent_scores_sha256'] or left['status']!='complete' or right['status']!='complete' or left['definitions']!=right['definitions'] or left['protocol_sha256']!=right['protocol_sha256'] or left['run']!=str(a.run.resolve()) or right['run']!=str(basepath.parent.resolve()):raise ValueError('Mismatched state evidence')
    select=lambda d,mode:{r['target_id']:r for r in d['rows'] if r['setting']=='cfg1/'+mode}
    metrics={mode:comparisons(select(left,mode),select(right,mode)) for mode in ('raw','latent')};g=gates(metrics['latent']);d=dict(status='complete',protocol_sha256=sha(protocol),metrics=metrics,sampling_quality_passed=g['sampling_quality'],diversity_gain_rule_passed=g['training_diversity'],cost=audit,scores_sha256=sha(a.scores),baseline_scores_sha256=sha(rightpath))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Antithetic versus IID external sampling','','Same compact500 weights,32 outputs, guidance, precision, seed, decoder noise and retry cap; latent Gaussian draws differ only through sign pairing. All48 families and all16 eligible state families. Positive-draw and output-integrity controls passed.','','| Selected metric | Antithetic | IID | Difference |95% family interval |','|---|---:|---:|---:|---|']
    for key,r in metrics['latent'].items():lines.append(f"| {key} | {r['candidate']:.5f} | {r['reference']:.5f} | {r['candidate_minus_reference']:+.5f} | {r['ci95']} |")
    lines+=['',f"Sampling quality:{d['sampling_quality_passed']}; declared diversity-gain follow-up criterion:{d['diversity_gain_rule_passed']}.",f"Attempted draws/output{audit['attempts_per_output']:.5f}; recovered{audit['recovered']}/{audit['initially_invalid']}, exhausted{audit['exhausted']}; generation{audit['initial_seconds']:.2f}s plus retries{audit['retry_seconds']:.2f}s.",'','MD W1 is better when lower. These development comparisons do not establish equilibrium populations. No end-to-end latency claim from generation-only timing. No pairing/temperature/seed-search grid. Locked tests unscored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
