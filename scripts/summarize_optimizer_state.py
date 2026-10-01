"""Evaluate a matched fresh-versus-restored optimizer-history continuation pair."""
import argparse, hashlib, json
from pathlib import Path
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores, means_by_target, hardware
from summarize_pilot import validate_training_evaluation, geometry_by_target, METRICS


def validate_pair(fresh, restored):
    for mode, training in [('fresh', fresh), ('restored', restored)]:
        cfg=training['config'];init=training['initialization']
        if training['status']!='complete' or training['steps']!=500 or cfg['updates']!=500:
            raise ValueError('incomplete training')
        if cfg['optimizer_state_experiment']!=mode or init['optimizer_state']!=mode:
            raise ValueError('optimizer treatment differs')
        if init['model_weights']!='saved_raw' or init['ema_weights']!='saved_ema' or init['exact_resume']:
            raise ValueError('initial model/EMA policy differs')
        if init['optimizer_initial_step']!=(init['historical_step'] if mode=='restored' else 0):
            raise ValueError('optimizer counter differs')
        if init['observed_optimizer_steps']!=([init['historical_step']] if mode=='restored' else []):
            raise ValueError('actual optimizer history differs')
        if [r['step'] for r in training['rows']]!=list(range(1,500,20))+[500]:
            raise ValueError('training trace is incomplete')
        if training['task']['arm']!='flow' or len(training.get('gradient_controls',[]))!=4 or not all(r['passed'] for r in training['gradient_controls']):
            raise ValueError('missing training controls')
    comparable=lambda t:{k:v for k,v in t['config'].items() if k!='optimizer_state_experiment'}
    if comparable(fresh)!=comparable(restored) or fresh['task']['seed']!=restored['task']['seed']:
        raise ValueError('additional training-protocol change')
    signature=lambda t:[tuple(r[k] for k in ('step','bucket','batch','flow_rng_sha256','input_ids_sha256')) for r in t['rows']]
    if signature(fresh)!=signature(restored):raise ValueError('paired batches or stochastic draws differ')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=dict(status='incomplete',runs={},failures=[],screen_passed=False,accuracy_promotion=False)
    found={}
    for run in a.runs:
        try:
            t=json.loads((run/'training.json').read_text());m=json.loads((run/'evaluation/manifest.json').read_text());s=json.loads((run/'evaluation/scores.json').read_text())
            validate_training_evaluation(t,m,s);mode=t['config']['optimizer_state_experiment']
            if mode in found:raise ValueError('duplicate optimizer treatment')
            found[mode]=(t,m,s)
            row=dict(task=t['task'],initialization=t['initialization'],accuracy=s['summaries']['steps25_cfg2'],training_seconds=t['training_seconds'],peak_reserved_gib=t['peak_reserved_bytes']/2**30)
            try:row['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),t['batches'],prefix='train::')
            except Exception as error:row['hardware']=dict(status='unavailable',error=str(error))
            result['runs'][run.name]=row
        except Exception as error:result['failures'].append(dict(run=str(run),error=f'{type(error).__name__}: {error}'))
    if set(found)=={'fresh','restored'} and not result['failures']:
        try:
            ft,fm,fs=found['fresh'];rt,rm,rs=found['restored'];validate_pair(ft,rt);cfg=ft['config']
            ref=Path(cfg['reference_run']);bm=json.loads((ref/'manifest.json').read_text());bs=json.loads((ref/'scores.json').read_text());validate_scores(bm,bs)
            sig=lambda m,s:(m['dataset'],m['decoder_checkpoint'],m['precision'],s['usalign'])
            if sig(fm,fs)!=sig(rm,rs) or sig(fm,fs)!=sig(bm,bs):raise ValueError('evaluation provenance differs')
            cp=Path(cfg['development_clusters'])
            if hashlib.sha256(cp.read_bytes()).hexdigest()!=cfg['development_clusters_sha256']:raise ValueError('clusters changed')
            clusters=json.loads(cp.read_text())['clusters'];setting='steps25_cfg2'
            result['paired']={metric:paired_comparison(means_by_target(fs['records'],setting,metric),means_by_target(rs['records'],setting,metric),clusters=clusters) for metric in METRICS}
            result['vs_untouched']={mode:{metric:paired_comparison(means_by_target(bs['records'],setting,metric),means_by_target(s['records'],setting,metric),clusters=clusters) for metric in METRICS} for mode,(_,_,s) in found.items()}
            result['geometry']={field:paired_comparison(geometry_by_target(fs['records'],field),geometry_by_target(rs['records'],field),clusters=clusters) for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
            result.update(status='complete',screen_passed=result['paired']['tm_fixed_reference']['theirs_minus_ours']>=.002 and result['vs_untouched']['restored']['tm_fixed_reference']['theirs_minus_ours']>=0)
        except Exception as error:result['failures'].append(dict(error=f'{type(error).__name__}: {error}'))
    lines=['# Optimizer-history continuation diagnostic','',
        'Both arms start from saved raw model weights and saved EMA. Only AdamW moments and bias-correction step counters differ: fresh versus restored. Same beta2=0.95, pilot data, per-protein loss, learning-rate schedule, batches and training seed. The original RNG/data stream and learning-rate schedule are not resumed.','',
        f"Status: {result['status']}. Eligible for two additional matched training seeds: {result['screen_passed']}. No independent-test scoring.",'']
    if result.get('paired'):
        tm=result['paired']['tm_fixed_reference']
        lines.append(f"TM: fresh {tm['ours']:.5f}, restored {tm['theirs']:.5f}, paired change {tm['theirs_minus_ours']:+.5f}, 95% cluster interval {tm['ci95']}.")
    lines+=['','A single development pair does not establish an accuracy improvement. Retain the +0.01 accuracy-promotion threshold, training-seed replication and independent confirmation.','', '```json',json.dumps(result,indent=2),'```']
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
