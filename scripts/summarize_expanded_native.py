"""Replicated accuracy transfer, retaining every trained seed and prior."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change


def analyze(m):
    c=m['config']
    for key in ('selection','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']}
    settings=[(h,g) for h in protocol['heads'] for g in protocol['guidance_by_head'][h]]
    if len(families)!=64 or len(set(families.values()))!=64 or len(settings)!=5 or [h['name'] for h in c['heads']]!=protocol['heads'] or c['training_family_count']!=122 or c['training_checkpoint_step'] not in (500,2000) or m['training_updates_executed']!=0:raise ValueError('wrong replicated screen scope')
    expected={(h,g,l) for h,g in settings for l in (128,256,384,512)}
    controls=m['controls']
    if len(controls)!=len(expected) or {(r['head'],r['guidance'],r['length']) for r in controls}!=expected or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('incomplete or failed batching controls')
    expected={(h,g,i,k) for h,g in settings for i in families for k in range(3)};rows=m['scores']
    if len(rows)!=len(expected) or {(r['head'],r['guidance'],r['target_id'],r['sample']) for r in rows}!=expected:raise ValueError('missing or duplicate scores')
    if any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in rows for k in ('ca_lddt','coarse_valid')):raise ValueError('invalid scores')
    values={(h,g):{key:{i:float(np.mean([r[key] for r in rows if (r['head'],r['guidance'],r['target_id'])==(h,g,i)])) for i in families} for key in ('ca_lddt','coarse_valid')} for h,g in settings}
    def compare(a,b):return {k:paired_change(values[a][k],values[b][k],families=families) for k in ('ca_lddt','coarse_valid')}
    arms=protocol.get('comparison_arms',['empirical','balanced'])
    if arms not in (['empirical','balanced'],['full','tail']):raise ValueError('unsupported comparison arms')
    if protocol['heads']!=['original']+[f'seed{seed}_{arm}' for seed in protocol['seeds'] for arm in arms] or len(set(protocol['seeds']))!=2:raise ValueError('both paired seeds required')
    effect='adaptation_effects' if arms==['full','tail'] else 'prior_effects'
    d=dict(step=c['training_checkpoint_step'],summaries={});d[effect]={}
    for h,g in settings:
        metrics=compare((h,g),('original',2));d['summaries'][h+f'_cfg{g}']=dict(versus_original_cfg2=metrics,quality_passed=bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01))
    for seed in protocol['seeds']:d[effect][str(seed)]=compare((f'seed{seed}_{arms[1]}',1),(f'seed{seed}_{arms[0]}',1))
    d['replicated_quality_passed']=all(d['summaries'][f'seed{seed}_{arms[1]}_cfg1']['quality_passed'] for seed in protocol['seeds'])
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':
        d.update(analyze(m));d['manifest_sha256']=sha(path)
        try:
            from summarize_comparison import hardware
            d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete evaluation')
    lines=['# Replicated122-family training: separate accuracy transfer','',f"Status: {d['status']}; checkpoint {d.get('step')}.",'','64 separate tuning families, three paired samples. Both priors and optimization seeds retained at CFG1 versus original CFG2. Euler25/decoder3, strict FP32. AFDB references are predictions. No independent-test scoring. Unadjusted family intervals; invalid samples remain included.','','| Head | CA-lDDT | Difference |95% interval | Valid fraction | Validity difference | Qualified |','|---|---:|---:|---|---:|---:|---|']
    for name,r in d.get('summaries',{}).items():
        ca=r['versus_original_cfg2']['ca_lddt'];v=r['versus_original_cfg2']['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['quality_passed']} |")
    for seed,r in d.get('prior_effects',{}).items():lines+=['',f"Seed{seed}, balanced minus empirical: CA-lDDT {r['ca_lddt']['difference']:+.5f},95% interval {r['ca_lddt']['ci95']}; validity {r['coarse_valid']['difference']:+.5f}."]
    if 'adaptation_effects' in d:
        lines[0]='# Restricted adaptation: separate accuracy transfer'
        lines[4]='64 separate tuning families, three paired samples. Full-network and restricted-tail balanced training at both seeds, CFG1 versus original CFG2. Euler25/decoder3, strict FP32. AFDB references are predictions. No independent-test scoring. Unadjusted family intervals; invalid samples remain included.'
        for seed,r in d['adaptation_effects'].items():lines+=['',f"Seed{seed}, tail minus full: CA-lDDT {r['ca_lddt']['difference']:+.5f},95% interval {r['ca_lddt']['ci95']}; validity {r['coarse_valid']['difference']:+.5f}."]
    if 'error' in d:lines+=['',d['error']]
    else:lines+=['',f"Both candidate seeds qualify: {d['replicated_quality_passed']}. External experimental-state ensembles remain a separate test; no model promotion."]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
