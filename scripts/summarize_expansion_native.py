"""Quality of both larger-data seeds on the unchanged64-family tuning panel."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change


def analyze(m):
    c=m['config']
    for key in ('selection','protocol','capacity_report'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    p=json.loads(Path(c['protocol']).read_text());capacity=json.loads(Path(c['capacity_report']).read_text());families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']}
    heads=['original']+[f'seed{s}_expansion' for s in (2026100171,2026100181)];settings=[('original',2)]+[(h,1) for h in heads[1:]]
    if p['heads']!=heads or [h['name'] for h in c['heads']]!=heads or p['guidance_by_head']!={h:[g] for h,g in settings} or p['seeds']!=[2026100171,2026100181]:raise ValueError('wrong paired head settings')
    if len(families)!=64 or len(set(families.values()))!=64 or c['training_family_count']<=122 or capacity['training_targets']!=c['training_family_count'] or c['training_checkpoint_step'] not in (500,2000) or capacity['step']!=c['training_checkpoint_step'] or not capacity['matched'] or m['training_updates_executed']!=0:raise ValueError('wrong expansion scope')
    controls=m['controls'];expected={(h,g,b) for h,g in settings for b in (128,256,384,512)}
    if len(controls)!=12 or {(r['head'],r['guidance'],r['length']) for r in controls}!=expected or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('missing/failed batching controls')
    scores=m['scores'];expected={(h,g,i,k) for h,g in settings for i in families for k in range(3)}
    if len(scores)!=576 or {(r['head'],r['guidance'],r['target_id'],r['sample']) for r in scores}!=expected or any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in scores for k in ('ca_lddt','coarse_valid')):raise ValueError('missing/invalid/duplicate scores')
    values={(h,g):{key:{i:float(np.mean([r[key] for r in scores if (r['head'],r['guidance'],r['target_id'])==(h,g,i)])) for i in families} for key in ('ca_lddt','coarse_valid')} for h,g in settings}
    d=dict(step=c['training_checkpoint_step'],training_targets=c['training_family_count'],summaries={})
    for h,g in settings:
        metrics={key:paired_change(values[h,g][key],values['original',2][key],families=families) for key in ('ca_lddt','coarse_valid')}
        d['summaries'][f'{h}_cfg{g}']=dict(versus_original_cfg2=metrics,quality_passed=bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01))
    d['replicated_quality_passed']=all(d['summaries'][h+'_cfg1']['quality_passed'] for h in heads[1:]);return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':d.update(analyze(m));d['manifest_sha256']=sha(path)
    else:d['error']=m.get('error','incomplete evaluation')
    lines=['# Larger-data tuning quality','',f"Status: {d['status']}; checkpoint{d.get('step')}.",'','Unchanged64-family tuning panel,3samples,FP32/Euler25/AE3. Both seeds retained; invalid samples remain included. No locked tests or model promotion.','','| Head | CA-lDDT | Difference |95% interval | Valid | Validity difference | Qualified |','|---|---:|---:|---|---:|---:|---|']
    for name,r in d.get('summaries',{}).items():
        ca=r['versus_original_cfg2']['ca_lddt'];v=r['versus_original_cfg2']['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['quality_passed']} |")
    lines+=['',f"Replicated quality: {d.get('replicated_quality_passed',False)}. Each qualified head still requires external diversity evaluation."]
    if d.get('error'):lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
