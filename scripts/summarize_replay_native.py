"""Native replay quality and same-seed effects, retaining all invalid structures."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change
from summarize_expansion_native import analyze as analyze_plain


def analyze(m):
    if m['status']!='complete':raise ValueError('incomplete native replay screen')
    c=m['config']
    for key in ('selection','protocol','capacity_report','plain_native_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());capacity=json.loads(Path(c['capacity_report']).read_text());families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']}
    seeds=[2026100171,2026100181];heads=['original']+[f'seed{s}_replay' for s in seeds];settings=[('original',2)]+[(h,1) for h in heads[1:]]
    if protocol['seeds']!=seeds or protocol['heads']!=heads or [h['name'] for h in c['heads']]!=heads or protocol['guidance_by_head']!={h:[g] for h,g in settings}:raise ValueError('wrong head settings')
    if len(families)!=64 or len(set(families.values()))!=64 or c['training_family_count']!=427 or c['replay_family_count']!=390 or capacity['training_targets']!=427 or capacity['seeds']!=seeds or capacity['step']!=c['training_checkpoint_step'] or not capacity['matched'] or not capacity['replicated_capacity_retained'] or m['training_updates_executed']!=0:raise ValueError('wrong replay evaluation scope')
    controls=m['controls'];expected={(h,g,b) for h,g in settings for b in (128,256,384,512)}
    if len(controls)!=12 or {(r['head'],r['guidance'],r['length']) for r in controls}!=expected or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('failed batching controls')
    scores=m['scores'];expected={(h,g,i,k) for h,g in settings for i in families for k in range(3)}
    if len(scores)!=576 or {(r['head'],r['guidance'],r['target_id'],r['sample']) for r in scores}!=expected or any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in scores for k in ('ca_lddt','coarse_valid')):raise ValueError('missing/invalid/duplicate samples')
    plain=json.loads(Path(c['plain_native_manifest']).read_text());plain_evidence=analyze_plain(plain)
    if plain['status']!='complete' or plain_evidence['step']!=c['training_checkpoint_step'] or plain['config']['selection_sha256']!=c['selection_sha256'] or plain['config']['evaluation_seed']!=c['evaluation_seed']:raise ValueError('wrong plain comparator')
    def original(rows):return {(r['target_id'],r['sample']):(r['ca_lddt'],r['coarse_valid']) for r in rows if r['head']=='original' and r['guidance']==2}
    actual,old=original(scores),original(plain['scores'])
    if set(actual)!=set(old) or any(not np.allclose(actual[k],old[k],atol=1e-6,rtol=0) for k in actual):raise ValueError('original heads disagree across native screens')
    def values(rows,h,g,key):return {i:float(np.mean([r[key] for r in rows if (r['head'],r['guidance'],r['target_id'])==(h,g,i)])) for i in families}
    d=dict(step=c['training_checkpoint_step'],training_targets=427,replay_targets=390,summaries={})
    for h,g in settings:
        metrics={key:paired_change(values(scores,h,g,key),values(scores,'original',2,key),families=families) for key in ('ca_lddt','coarse_valid')}
        result=dict(versus_original_cfg2=metrics,quality_passed=bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01))
        if h!='original':result['versus_plain427']={key:paired_change(values(scores,h,g,key),values(plain['scores'],h.replace('_replay','_expansion'),1,key),families=families) for key in ('ca_lddt','coarse_valid')}
        d['summaries'][f'{h}_cfg{g}']=result
    d['replicated_quality_passed']=all(d['summaries'][h+'_cfg1']['quality_passed'] for h in heads[1:]);return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':d.update(analyze(m));d['manifest_sha256']=sha(path)
    else:d['error']=m.get('error','incomplete')
    lines=['# Functional replay native quality','',f"Status:{d['status']}; checkpoint{d.get('step')}.427 teacher families plus390 disjoint anchor training families; unchanged64-family native tuning panel and3samples. All failures retained, locked tests unscored.",'','| Head | CA-lDDT | CA difference |95% interval | Valid | Validity difference | Qualified |','|---|---:|---:|---|---:|---:|---|']
    for name,r in d.get('summaries',{}).items():
        ca=r['versus_original_cfg2']['ca_lddt'];v=r['versus_original_cfg2']['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['quality_passed']} |")
    for name,r in d.get('summaries',{}).items():
        if 'versus_plain427' in r:
            v=r['versus_plain427'];lines+=['',f"{name} versus same-step plain427: CA difference{v['ca_lddt']['difference']:+.5f},95% interval{v['ca_lddt']['ci95']}; validity difference{v['coarse_valid']['difference']:+.5f}."]
    lines+=['',f"Replicated native quality:{d.get('replicated_quality_passed',False)}. Each individually qualified head still requires external diversity evaluation."]
    if d.get('error'):lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
