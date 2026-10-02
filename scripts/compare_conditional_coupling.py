"""Matched coupling comparison, including all archived prediction/state audits."""
import argparse,copy,json
from pathlib import Path
import h5py,numpy as np,torch
from summarize_conditional_coupling import audit
from latentfold.teacher_states import audited_families,paired_change
from compare_overfit_balanced import scored
from train_overfit import score_ensemble
from audit_distill_labels import metrics
from prepare_overfit import sha


def compare(runs):
 arms={};configs=[];torch.set_num_threads(1)
 for run in runs:
  audit(run);m=json.loads((run/'manifest.json').read_text());c=copy.deepcopy(m['config']);arm=c['conditional_coupling'].pop('arm')
  if arm in arms or m['status']!='complete' or m['updates']!=500 or c['profile_only']:raise ValueError('Incomplete matched arms')
  arms[arm]=(run,m);configs.append(c)
 if set(arms)!={'independent','optimal'} or configs[0]!=configs[1]:raise ValueError('Recipe differs beyond pairing')
 c=configs[0];left,right=[arms[k][1] for k in ('independent','optimal')]
 if left['initial_checkpoint_sha256']!=right['initial_checkpoint_sha256']:raise ValueError('Different initialization')
 fields=('step','ids_sha256','labels_sha256','noise_sha256','targets_sha256','times_sha256','dropout_sha256','flow_rng_sha256','global_rng_sha256')
 if [{k:r[k] for k in fields} for r in left['coupling_updates']]!=[{k:r[k] for k in fields} for r in right['coupling_updates']]:raise ValueError('Matched draws or RNG states differ')
 fields=('step','length','batch','learning_rate','ids_sha256','label_choices_sha256')
 if [{k:r[k] for k in fields} for r in left['training']]!=[{k:r[k] for k in fields} for r in right['training']]:raise ValueError('Training schedules differ')
 families=audited_families(c);source=json.loads(Path(c['label_manifest']).read_text());targets={r['id']:r for r in source['config']['targets']};labels=Path(c['label_manifest']).parent/'labels.h5'
 if sha(labels)!=source['labels_sha256']:raise ValueError('Changed teacher arrays')
 checked=0;identity=[];score_keys=('valid_fraction','teacher_ca_lddt','reference_ca_lddt','teacher_feature_rmse','valid_teacher_hit_fraction','state_total_variation')
 with h5py.File(labels) as data:
  for arm,(run,m) in arms.items():
   if len(m['scores'])!=64 or len(m['controls'])!=4:raise ValueError('Incomplete evaluation/controls')
   for step in (0,500):
    with h5py.File(run/f'evaluation_{step}.h5') as f:
     if set(f)!=set(targets):raise ValueError('Archived target coverage changed')
     for ident in targets:
      g=data[ident];record=dict(state=json.loads(g.attrs['state_definition']),teacher_backbone=torch.from_numpy(g['teacher_backbone'][:]),reference_backbone=torch.from_numpy(g['reference_backbone'][:]));bb=torch.from_numpy(f[ident+'/cfg1/backbone'][:]);actual,_,_=score_ensemble(bb,record);saved=next(r for r in m['scores'] if (r['target_id'],r['guidance'],r['step'])==(ident,1,step))
      if actual['assignments']!=saved['assignments'] or actual['coverage']!=saved['coverage'] or actual['strict_coverage']!=saved['strict_coverage'] or any(abs(actual[k]-saved[k])>1e-5 for k in score_keys):raise ValueError('Archived structural/state score audit failed')
      checked+=len(bb)
  with h5py.File(arms['independent'][0]/'evaluation_0.h5') as a,h5py.File(arms['optimal'][0]/'evaluation_0.h5') as b:
   for ident in targets:
    x,y=[torch.from_numpy(f[ident+'/cfg1/backbone'][:]) for f in (a,b)];met=metrics(x,y);za,zb=[f[ident+'/cfg1/z'][:] for f in (a,b)];dz=float(np.max(abs(za-zb)));control=dict(target_id=ident,latent_max_abs=dz,max_ca_rmsd=float(met['ca_rmsd'].max()),min_ca_lddt=float(met['ca_lddt'].min()))
    if dz>1e-5 or control['max_ca_rmsd']>.2 or control['min_ca_lddt']<.99:raise ValueError('Initial output identity failed')
    identity.append(control)
 groups=dict(initial=scored(left,0,1,targets),independent=scored(left,500,1,targets),optimal=scored(right,500,1,targets));other_initial=scored(right,0,1,targets)
 if any(groups['initial'][i]['assignments']!=other_initial[i]['assignments'] for i in targets):raise ValueError('Initial state/validity assignment differs')
 keys=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','state_total_variation','balanced_state_tv');summaries={k:{metric:float(np.mean([r[metric] for r in rows.values()])) for metric in keys} for k,rows in groups.items()};comparisons={}
 for name in ('initial','independent'):comparisons[name]={key:paired_change({i:groups['optimal'][i][key] for i in families},{i:groups[name][i][key] for i in families},families=families) for key in keys}
 gain=comparisons['independent'];initial=comparisons['initial'];checks=dict(recall_vs_control=gain['coverage32']['ci95'][0]>0,recall_vs_initial=initial['coverage32']['ci95'][0]>0,validity=gain['valid_fraction']['difference']>=-.01,teacher_fidelity=gain['teacher_ca_lddt']['difference']>=-.005)
 return dict(status='complete',summaries=summaries,comparisons=comparisons,checks=checks,qualified_for_replication_and_native=all(checks.values()),archived_predictions_audited=checked,initial_identity=identity,seed=c['seed'],matched_updates=500,sources={str(run/'manifest.json'):sha(run/'manifest.json') for run in runs},scope='All32families are training data. Teacher states are predictions,not biological populations. No independent tests or promotion.')


def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=compare(a.runs);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Matched conditional noise/teacher coupling','',d['scope'],'','All500target/label/noise/time/dropout/RNG traces matched; all4096archived predictions and initial output identity audited.','', '| Arm | Recall@32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | Balanced TV |','|---|---:|---:|---:|---:|---:|']
 for arm,r in d['summaries'].items():lines.append(f"| {arm} | {r['coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['reference_ca_lddt']:.5f} | {r['balanced_state_tv']:.5f} |")
 for name,r in d['comparisons'].items():lines+=['',f"Optimal minus{name}: recall {r['coverage32']['difference']:+.5f},95%family interval {r['coverage32']['ci95']}; validity {r['valid_fraction']['difference']:+.5f}."]
 lines+=['',f"Qualified for replication/native screen: {d['qualified_for_replication_and_native']}. Checks: {d['checks']}."];a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
