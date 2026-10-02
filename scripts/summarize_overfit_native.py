"""Report every matched head's tuning accuracy and the cost of balancing states."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import paired_change
from prepare_overfit import sha
from summarize_comparison import hardware


def analyze(m):
    c=m['config']
    if sha(c['selection'])!=c['selection_sha256'] or sha(c['protocol'])!=c['protocol_sha256']:raise ValueError('changed panel/protocol')
    families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']};heads=json.loads(Path(c['protocol']).read_text())['heads']
    if len(families)!=64 or len(set(families.values()))!=64 or [h['name'] for h in c['heads']]!=heads or len(m['scores'])!=1920 or len(m['controls'])!=40 or m['training_updates_executed']!=0:raise ValueError('incomplete transfer evaluation')
    expected={(head,guidance,length) for head in heads for guidance in (1,2) for length in (128,256,384,512)}
    if {(r['head'],r['guidance'],r['length']) for r in m['controls']}!=expected or any(not np.isfinite(r['ca_rmsd']) or not np.isfinite(r['ca_lddt']) or r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in m['controls']):raise ValueError('invalid batching controls')
    values={}
    for head in heads:
        for guidance in (1,2):
            rows=[r for r in m['scores'] if r['head']==head and r['guidance']==guidance]
            if len(rows)!=192 or {r['target_id'] for r in rows}!=set(families) or any(sorted(r['sample'] for r in rows if r['target_id']==i)!=[0,1,2] for i in families):raise ValueError('incomplete head/guidance')
            if any(not np.isfinite(r[k]) for r in rows for k in ('ca_lddt','coarse_valid')):raise ValueError('nonfinite scores')
            values[head,guidance]={key:{i:float(np.mean([r[key] for r in rows if r['target_id']==i])) for i in families} for key in ('ca_lddt','coarse_valid')}
    def compare(a,b):return {key:paired_change(values[a][key],values[b][key],families=families) for key in ('ca_lddt','coarse_valid')}
    d=dict(summaries={},prior_effects={})
    for head in heads:
        for guidance in (1,2):
            metrics=compare((head,guidance),('original',2));matched=compare((head,guidance),('original',guidance))
            d['summaries'][f'{head}_cfg{guidance}']=dict(versus_original_cfg2=metrics,versus_original_matched_cfg=matched,quality_passed=bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01))
    for frame in ('aligned_teacher','pca_teacher'):
        for guidance in (1,2):d['prior_effects'][f'{frame}_cfg{guidance}']=compare((frame+'_balanced',guidance),(frame+'_empirical',guidance))
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json'
    m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':
        d.update(analyze(m));d['manifest_sha256']=sha(path)
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
    else:d['error']=m.get('error','Incomplete evaluation')
    lines=['# Accuracy transfer from32-protein capacity training','',f"Status: {d['status']}.",'',
           'All four matched500-update teacher checkpoints and the original model;64 separate tuning families,three paired seeds,CFG1/2,Euler25,decoder3,strict FP32. References are AFDB predictions. No locked-test scoring. All settings and geometry failures remain included. Family intervals are unadjusted. This measures transfer from a small training panel, not independent-test performance or biological populations.','',
           '| Head / CFG | CA-lDDT | Delta versus original CFG2 | 95% interval | Valid | Validity delta | Quality gate |','|---|---:|---:|---|---:|---:|---|']
    for name,r in d.get('summaries',{}).items():
        ca=r['versus_original_cfg2']['ca_lddt'];v=r['versus_original_cfg2']['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['quality_passed']} |")
    lines+=['','| Balanced minus empirical at matched frame/CFG | CA-lDDT difference | 95% interval | Validity difference |','|---|---:|---|---:|']
    for name,r in d.get('prior_effects',{}).items():lines.append(f"| {name} | {r['ca_lddt']['difference']:+.5f} | {r['ca_lddt']['ci95']} | {r['coarse_valid']['difference']:+.5f} |")
    if 'error' in d:lines+=['',d['error']]
    lines+=['','Training-capacity gains do not imply generalization. A qualified model still needs separate ensemble development assessment and training-seed replication before promotion. Both scheduled2000-update endpoints retain their original budgets.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
