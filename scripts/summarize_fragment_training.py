"""Independently recompute every raw fragment score, retaining all failures."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_error
from prepare_overfit import sha


def interval(values):
    x=np.asarray(values,float);rng=np.random.default_rng(2026100233);means=x[rng.integers(0,len(x),(10000,len(x)))].mean(1)
    return dict(mean=float(x.mean()),ci95=np.quantile(means,[.025,.975]).tolist(),families=len(x))


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),updates=m.get('updates',0),profile_qualified=False)
    c=m['config'];warm=c.get('warm_start',False)
    if bool(c.get('conditional_time_shift'))!=bool(c.get('time_protocol')):raise ValueError('Unbound conditional time shift')
    if c.get('time_protocol'):
        from fragment_time_shift import audit_config
        audit_config(c)
    if c.get('augmentation_protocol'):
        from fragment_teacher_augmentation_training import audit_config
        audit_config(c)
    if c.get('extension_protocol'):
        from fragment_extension import audit_extension
        audit_extension(c)
    if warm:
        for key in ('warm_protocol','warm_parent_manifest','warm_parent_report','warm_predictions'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed continuation source')
        controls=m['warm_controls']
        if len(controls)!=(32 if c['profile_only'] else 384) or any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in controls):raise ValueError('Warm-start parity failed')
    if c.get('weight_breadth_protocol'):
        from fragment_weight_breadth import audit
        audit(c)
    if c.get('latent_motif_weight') and not c.get('weight_breadth_protocol'):
        if not warm or c.get('training_protein_count')!=128 or sha(c['latent_weight_protocol'])!=c['latent_weight_protocol_sha256'] or c['latent_motif_weight']!=json.loads(Path(c['latent_weight_protocol']).read_text())['weight']:raise ValueError('Invalid latent motif weighting')
    if c.get('backbone_tokens'):
        if warm or c['arm']!='full' or c.get('fragment_representation') or sha(c['backbone_tokens_protocol'])!=c['backbone_tokens_protocol_sha256'] or not m.get('shared_adapter_initial'):raise ValueError('Invalid backbone-token contrast')
    if c.get('fragment_representation'):
        if c['fragment_representation']!='geometry_sequence' or warm or c['arm']!='full' or sha(c['representation_protocol'])!=c['representation_protocol_sha256'] or m.get('representation_latent_max_abs')!=0:raise ValueError('Invalid representation contrast')
    if c.get('expanded_fragment_data'):
        if not warm or sha(c['expanded_protocol'])!=c['expanded_protocol_sha256']:raise ValueError('Invalid expanded continuation')
        parent_config=json.loads(Path(c['warm_parent_manifest']).read_text())['config']
        with h5py.File(parent_config['fragments']) as original:
            from fragment_extension import validate_capacity_panel
            validate_capacity_panel(c,parent_config,original['train'])
    for key in ('protocol','data_report','data_manifest','fragments','checkpoint','decoder_checkpoint','initial_manifest','initial_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if c.get('variant')=='geometry':
        if sha(c['geometry_protocol'])!=c['geometry_protocol_sha256'] or len(m['geometry_controls'])!=(8 if c.get('distance_precision')=='fp64' else 4)*(len(c['evaluation_steps'])+1) or any(r['pose_latent_max_abs']>1e-4 for r in m['geometry_controls']):raise ValueError('Geometry conditioner controls failed')
    if c.get('distance_precision')=='fp64':
        if sha(c['geometry_precision_protocol'])!=c['geometry_precision_protocol_sha256'] or sha(c['pose_diagnostic_report'])!=c['pose_diagnostic_report_sha256']:raise ValueError('Changed precision correction evidence')
    if c.get('variant')=='geometry' and c['arm']=='full':
        for key in ('geometry_full_protocol','geometry_frozen_report','geometry_designability_report'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed full geometry evidence')
    if c.get('auxiliary_motif'):
        if sha(c['motif_objective_protocol'])!=c['motif_objective_protocol_sha256'] or sha(c['motif_baseline_report'])!=c['motif_baseline_report_sha256']:raise ValueError('Changed objective provenance')
        rows=m['motif_objective_updates']
        if len(rows)!=c['updates'] or [r['step'] for r in rows]!=list(range(1,c['updates']+1)) or any(not np.isfinite(r['motif_mse']) or r['aux_to_flow_ratio']>c['auxiliary_motif']['maximum_gradient_ratio']+1e-7 or r['flow_parameter_grad_norm']<=0 for r in rows):raise ValueError('Incomplete/unbounded motif gradients')
        if sum(r['motif_examples'] for r in rows)<c['updates'] or not any(r['aux_parameter_grad_norm']>0 for r in rows):raise ValueError('Insufficient motif objective exposure')
    if c.get('target_frame_training'):
        from frame_target_audit import audit_frame_targets
        if c.get('rollout_motif') or c.get('expanded_fragment_data') or c['updates']!=(40 if c['profile_only'] else 500) or c['evaluation_steps']!=([40] if c['profile_only'] else [500]):raise ValueError('Invalid target-frame schedule')
        audit_frame_targets(m)
    if c.get('rollout_breadth_protocol'):
        if not c.get('expanded_fragment_data') or not c.get('rollout_motif'):raise ValueError('Invalid breadth/objective combination')
        for key in ('rollout_breadth_protocol','rollout_breadth_gate_report','rollout_breadth_gate_manifest','rollout_control_manifest'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed breadth/objective source')
    if c.get('rollout_pilot'):
        if not c.get('rollout_motif') or c['profile_only'] or c['updates']!=500 or c['evaluation_steps']!=[500]:raise ValueError('Invalid pilot schedule')
        for key in ('rollout_pilot_protocol','rollout_control_manifest'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed pilot source')
    if c.get('rollout_motif'):
        if sha(c['rollout_protocol'])!=c['rollout_protocol_sha256'] or c['rollout_motif']!=json.loads(Path(c['rollout_protocol']).read_text())['auxiliary']:raise ValueError('Changed rollout provenance')
        controls=m['rollout_controls'];rows=m['rollout_objective_updates']
        if len(controls)!=4 or {r['target_id'] for r in controls}!=set(c['control_ids']) or any(not np.isfinite(r['latent_max_abs']) or r['latent_max_abs']>1e-5 for r in controls):raise ValueError('Rollout sampler parity failed')
        if len(rows)!=c['updates'] or [r['step'] for r in rows]!=list(range(1,c['updates']+1)) or any(not np.isfinite(r['motif_mse']) or r['aux_to_flow_ratio']>c['rollout_motif']['maximum_gradient_ratio']+1e-7 or r['flow_parameter_grad_norm']<=0 for r in rows):raise ValueError('Incomplete/unbounded rollout gradients')
        if sum(r['motif_examples'] for r in rows)<c['updates'] or not any(r['aux_parameter_grad_norm']>0 for r in rows) or any(r['motif_examples'] and r['velocity_evaluations']!=50 for r in rows):raise ValueError('Incomplete rollout objective')
    if m['updates']!=c['updates'] or len(m['training'])!=c['updates'] or m['frozen_initial']!=m['frozen_final']:raise ValueError('Incomplete/frozen-weight failure')
    if [r['step'] for r in m['training']]!=list(range(1,c['updates']+1)) or any(not np.isfinite(r['flow_loss']) or r['adapter_gradient_norm']<=0 for r in m['training']):raise ValueError('Invalid training trace')
    if any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in m['initial_controls']):raise ValueError('Failed initial controls')
    if len(m['initial_controls'])!=(32 if c['profile_only'] else 128) or len(m['sampling_controls'])!=4 or any(r['original_max_abs']>1e-5 or r['batched_max_abs']>(1e-5 if c.get('sampling_control_mode')=='same_batch_repeat' else 1e-4) or (c.get('sampling_control_mode')=='same_batch_repeat' and r.get('kind')!='same_batch_repeat') for r in m['sampling_controls']):raise ValueError('Incomplete sampler controls')
    summaries=[];audited=0
    with h5py.File(c['fragments']) as src,h5py.File(c['initial_predictions']) as initial,h5py.File(c['warm_predictions'] if warm else c['initial_predictions']) as historical:
        expected={(cohort,mode,ident,k) for cohort in ('train','development') for ident in src[cohort] for mode in ('conditioned','null') for k in range(4) if (not c['profile_only'] or cohort=='development' and ident in c['control_ids']) and (cohort!='train' or 'evaluation_train_ids' not in c or ident in c['evaluation_train_ids'])}
        if [e['step'] for e in m['evaluations']]!=[0]+c['evaluation_steps']:raise ValueError('Missing evaluation')
        for e in m['evaluations']:
            index={(r['cohort'],r['mode'],r['target_id'],r['slot']):r for r in e['scores']}
            if set(index)!=expected or len(index)!=len(e['scores']):raise ValueError('Missing/duplicate outputs')
            diversity={}
            with h5py.File(run/f"evaluation_{e['step']}.h5") as f:
                for cohort,mode,ident in sorted({key[:3] for key in expected}):
                    g=src[cohort+'/'+ident];q=g['conditions/f30_center'];ref=g['reference_backbone'][:] if cohort=='train' else initial['references/'+ident+'/backbone'][:];bb=f[f'{cohort}/{mode}/{ident}/backbone'][:];z=f[f'{cohort}/{mode}/{ident}/latent'][:];fragment=q['fragment'][:];st=int(q.attrs['start']);k=len(fragment)
                    if bb.shape!=(4,len(ref),4,3) or z.shape!=(4,len(ref),8) or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Invalid saved output')
                    geom=backbone_geometry(bb);err=motif_error(bb[:,st:st+k],fragment,np.ones(k,bool));diversity[(cohort,mode,ident)]=float(np.mean([ca_metrics(bb[i,:,1],bb[j,:,1])['ca_rmsd'] for i in range(4) for j in range(i)]))
                    for slot in range(4):
                        old=index[(cohort,mode,ident,slot)];metrics=ca_metrics(bb[slot,:,1],ref[:,1])
                        if abs(old['motif_drms']-err[slot])>1e-6 or old['coarse_valid']!=int(geom['coarse_valid'][slot]) or any(abs(old[key]-value)>1e-6 for key,value in metrics.items()):raise ValueError('Saved-score mismatch')
                        if (cohort=='development' or warm) and (e['step']==0 or c['arm']=='adapter_only' and mode=='null'):
                            history_path=f'{cohort}/{mode}/{ident}' if warm else 'original50/unconditional/'+ident
                            original=historical[history_path+'/backbone'][slot];control=ca_metrics(bb[slot,:,1],original[:,1])
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99 or np.max(abs(z[slot]-historical[history_path+'/latent'][slot]))>1e-5:raise ValueError('Saved historical parity failed')
                        audited+=1
            for cohort in sorted({key[0] for key in expected}):
                families=sorted({r['family'] for r in e['scores'] if r['cohort']==cohort});arms={};paired=[]
                for mode in ('conditioned','null'):
                    rows=[r for r in e['scores'] if (r['cohort'],r['mode'])==(cohort,mode)];arms[mode]=dict(samples=len(rows),raw_valid_fraction=float(np.mean([r['coarse_valid'] for r in rows])),motif_fraction_under_1A=float(np.mean([r['motif_drms']<=1 for r in rows])),joint_fraction=float(np.mean([r['coarse_valid'] and r['motif_drms']<=1 for r in rows])),mean_motif_drms=float(np.mean([r['motif_drms'] for r in rows])),mean_reference_ca_lddt=float(np.mean([r['ca_lddt'] for r in rows])),mean_pairwise_sample_ca_rmsd=float(np.mean([v for (co,mo,_),v in diversity.items() if (co,mo)==(cohort,mode)])))
                for family in families:
                    means=[np.mean([r['coarse_valid'] and r['motif_drms']<=1 for r in e['scores'] if (r['cohort'],r['mode'],r['family'])==(cohort,mode,family)]) for mode in ('conditioned','null')];paired.append(means[0]-means[1])
                summaries.append(dict(step=e['step'],cohort=cohort,arms=arms,conditioned_minus_null_joint=interval(paired)))
    memory=max(b['peak_reserved_bytes']/2**30 for b in m['batches']);gate=next((r['conditioned_minus_null_joint']['ci95'][0]>0 for r in summaries if r['step']==2000 and r['cohort']=='train'),False)
    result=dict(status='complete',config=c,manifest_sha256=sha(path),updates=m['updates'],total_training_updates=m['updates']+c.get('total_prior_updates',0),audited_predictions=audited,training_seconds=sum(b['seconds'] for b in m['batches']),evaluation_seconds=sum(e['seconds'] for e in m['evaluations']),elapsed_seconds=m['elapsed_seconds'],max_reserved_GiB=memory,profile_qualified=c['profile_only'] and memory<=75,capacity_gate_passed=None if c.get("rollout_pilot") or c.get("target_frame_training") else gate,summaries=summaries,initial_controls=len(m['initial_controls']),sampling_controls=len(m['sampling_controls']))

    if c.get('time_protocol'):
        from fragment_time_shift import compare
        result['time_contrast_audit']=compare(Path(__file__).resolve().parents[1],run)
    if c.get('augmentation_protocol'):
        from fragment_teacher_augmentation_training import compare
        result['augmentation_contrast_audit']=compare(Path(__file__).resolve().parents[1],run)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='config'};a.output.with_suffix('.md').write_text('# Explicit isolated-fragment conditioning\n\nRaw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')

if __name__=='__main__':main()
