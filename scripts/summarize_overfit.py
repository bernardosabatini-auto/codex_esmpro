"""Summarize teacher-mode recall without claiming biological generalization."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');c=m.get('config',{});d=dict(status=m['status'],arm=c.get('arm'),profile_only=c.get('profile_only'),summaries={},paired={})
    if m['status']=='complete':
        if m['updates']!=c['updates']:raise ValueError('incomplete training')
        if not c.get('profile_only'):
            if len(m['scores'])!=(len(c['evaluation_steps'])+1)*32*2 or len(m['controls'])!=8:raise ValueError('incomplete evaluations')
            for guidance in (1,2):
                baseline={r['target_id']:r['coverage']['32'] for r in m['scores'] if r['step']==0 and r['guidance']==guidance}
                for step in [0]+c['evaluation_steps']:
                    rows=[r for r in m['scores'] if r['step']==step and r['guidance']==guidance]
                    if len(rows)!=32 or len({r['target_id'] for r in rows})!=32 or any(len(r['assignments'])!=32 for r in rows):raise ValueError('incomplete target/sample coverage')
                    key=f'{step}_cfg{guidance}';d['summaries'][key]={k:float(np.mean([r[k] for r in rows])) for k in ('valid_fraction','teacher_ca_lddt','reference_ca_lddt','teacher_feature_rmse','valid_teacher_hit_fraction','state_total_variation','teacher_sampling_expected_coverage32')};d['summaries'][key]['coverage32']=float(np.mean([r['coverage']['32'] for r in rows]));d['paired'][key]=paired_comparison({r['target_id']:r['coverage']['32'] for r in rows},baseline)
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3;d['training_seconds']=sum(r['seconds'] for r in m['batches'] if r['stage']=='training')
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as e:d['hardware']=dict(status='unavailable',error=str(e))
    else:d['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Small-ensemble learnability diagnostic','',f"Status: {d['status']}; arm: {d['arm']}; profile only: {d['profile_only']}.",'','32 training proteins selected for teacher diversity. Teacher-defined contact modes are predictions, not measured biological states. Fresh32-sample ensembles at both CFG settings; all samples retained. Coverage requires feature RMSE<=2A, nearest-contact teacher CA-lDDT>=0.8 and coarse-valid geometry.','', '| Updates / guidance | Mode recall @32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV (lower better) |','|---|---:|---:|---:|---:|---:|']
    for key,r in d['summaries'].items():lines.append(f"| {key} | {r['coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['reference_ca_lddt']:.5f} | {r['state_total_variation']:.5f} |")
    if 'error' in d:lines+=['',d['error']]
    lines+=['','This is a training-capacity experiment. No model promotion or unseen-family accuracy claim is possible from these scores.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
