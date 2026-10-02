"""Summarize teacher-mode recall without claiming biological generalization."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.teacher_states import paired_change,audited_families
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');c=m.get('config',{});d=dict(status=m['status'],arm=c.get('arm'),profile_only=c.get('profile_only'),summaries={},paired={},latent_diagnostics={})
    d['target_estimator']=c.get('target_estimator','sampled')
    d['label_distribution']=c.get('label_distribution','empirical')
    if m['status']=='complete':
        if m['updates']!=c['updates']:raise ValueError('incomplete training')
        if c.get('trainable_tail_blocks') is not None:
            d['training_subset']=m['training_subset']
            if not d['training_subset']['frozen_unchanged']:raise ValueError('frozen parameters changed')
        if c.get('local_geometry'):
            rows=m.get('local_geometry_updates',[])
            if len(rows)!=m['updates'] or {r['step'] for r in rows}!=set(range(1,m['updates']+1)):raise ValueError('incomplete local geometry gradient accounting')
            keys=('flow_parameter_grad_norm','aux_parameter_grad_norm','effective_geometry_weight','aux_to_flow_ratio','geometry_loss')
            if any(not np.isfinite(r[k]) or r[k]<0 for r in rows for k in keys) or any(r['flow_parameter_grad_norm']<=0 or r['aux_to_flow_ratio']>.100001 for r in rows):raise ValueError('invalid local geometry gradients')
            d['local_geometry']=dict(updates=len(rows),active_updates=sum(r['geometry_count']>0 for r in rows),positive_gradient_updates=sum(r['aux_parameter_grad_norm']>0 for r in rows),maximum_aux_to_flow_ratio=max(r['aux_to_flow_ratio'] for r in rows),mean_geometry_loss=float(np.mean([r['geometry_loss'] for r in rows])),active_buckets=sorted({r['length'] for r in rows if r['aux_parameter_grad_norm']>0}))
        if not c.get('profile_only'):
            families=audited_families(c)
            if c.get('evaluation_ids') is not None:
                ids=c['evaluation_ids']
                if c.get('corpus_kind')!='expansion' or len(ids)!=64 or len(set(ids))!=64 or not set(ids)<=set(families):raise ValueError('invalid evaluation panel')
                d['training_targets']=len(families);families={i:families[i] for i in ids};d['evaluated_targets']=len(families)
            guidance_settings=c.get('evaluation_guidance',(1,2));targets=len(families)
            if len(m['scores'])!=(len(c['evaluation_steps'])+1)*targets*len(guidance_settings) or len(m['controls'])!=4*len(guidance_settings):raise ValueError('incomplete evaluations')
            for guidance in guidance_settings:
                baseline={r['target_id']:r['coverage']['32'] for r in m['scores'] if r['step']==0 and r['guidance']==guidance}
                for step in [0]+c['evaluation_steps']:
                    rows=[r for r in m['scores'] if r['step']==step and r['guidance']==guidance]
                    if len(rows)!=targets or {r['target_id'] for r in rows}!=set(families) or any(len(r['assignments'])!=32 for r in rows):raise ValueError('incomplete target/sample coverage')
                    key=f'{step}_cfg{guidance}';d['summaries'][key]={k:float(np.mean([r[k] for r in rows])) for k in ('valid_fraction','teacher_ca_lddt','reference_ca_lddt','teacher_feature_rmse','valid_teacher_hit_fraction','state_total_variation','teacher_sampling_expected_coverage32')};d['summaries'][key]['coverage32']=float(np.mean([r['coverage']['32'] for r in rows]));d['paired'][key]=paired_change({r['target_id']:r['coverage']['32'] for r in rows},baseline,families=families)
                    d['latent_diagnostics'][key]={metric:float(np.mean([r['latent_diagnostic'][metric] for r in rows])) for metric in rows[0]['latent_diagnostic']}
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3;d['training_seconds']=sum(r['seconds'] for r in m['batches'] if r['stage']=='training')
        lengths=sorted(int(k) for k in c['batches']);schedule=m.get('length_schedule',[lengths[step%len(lengths)] for step in range(m['updates'])])
        if len(schedule)!=m['updates'] or set(schedule)-set(lengths):raise ValueError('invalid recorded length schedule')
        work=[(length,c['batches'][str(length)]) for length in schedule]
        d['training_examples']=sum(count for length,count in work);d['padded_residue_examples']=sum(length*count for length,count in work)
        d['examples_per_training_second']=d['training_examples']/d['training_seconds'];d['padded_residues_per_training_second']=d['padded_residue_examples']/d['training_seconds']
        if d['target_estimator']=='posterior':
            rows=m['training'];d['logged_posterior_variance_mean']=float(np.mean([r['posterior_variance'] for r in rows]));d['logged_posterior_floor_fraction']=float(np.mean([r['posterior_variance']/r['flow_loss'] for r in rows]))
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as e:d['hardware']=dict(status='unavailable',error=str(e))
    else:d['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Small-ensemble learnability diagnostic','',f"Status: {d['status']}; arm: {d['arm']}; profile only: {d['profile_only']}.",'','32 training proteins selected for teacher diversity. Teacher-defined contact modes are predictions, not measured biological states. Fresh32-sample ensembles at both CFG settings; all samples retained. Coverage requires feature RMSE<=2A, nearest-contact teacher CA-lDDT>=0.8 and coarse-valid geometry.','', '| Updates / guidance | Mode recall @32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV (lower better) |','|---|---:|---:|---:|---:|---:|']
    for key,r in d['summaries'].items():lines.append(f"| {key} | {r['coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['reference_ca_lddt']:.5f} | {r['state_total_variation']:.5f} |")
    if c.get('corpus_inventory'):
        lines[0]='# Expanded teacher-ensemble training diagnostic'
        lines[4]='All122 metadata-eligible training families, unchanged aligned labels, CFG1 ensembles. Teacher modes are predictions, not biological-state measurements. Full training draws length buckets proportional to target counts; the short profile cycles all buckets to test memory. All samples retained with unchanged geometry/state-hit criteria.'
        if c.get('corpus_kind')=='expansion':lines[4]=f"Larger metadata-eligible training corpus; fixed64-family training-capacity panel (original32 plus32 new). All families are training data. Proportional bucket sampling, CFG1/Euler25/decoder3. No unseen-family or biological-state claim; unchanged native/external gates remain separate. Training targets: {m.get('training_targets')}."
    lines+=['',f"Training label distribution: {d['label_distribution']}. The state-TV column always compares with the original empirical teacher prior; equal-state-prior TV is reported separately by analyze_overfit_states.py."]
    if d['latent_diagnostics']:
        lines+=['','Latent diagnostics (nearest teacher RMSE): global reference fits below are evaluation-only and never alter predictions.','','| Updates / guidance | Sampled latent | Re-encoded backbone | Pose-aligned re-encoded backbone | Decoder/encoder RMSE |','|---|---:|---:|---:|---:|']
        for key,r in d['latent_diagnostics'].items():lines.append(f"| {key} | {r['sampled_to_teacher_rmse']:.5f} | {r['reencoded_to_teacher_rmse']:.5f} | {r['pose_aligned_reencoded_to_teacher_rmse']:.5f} | {r['decoder_encoder_rmse']:.5f} |")
    if 'error' in d:lines+=['',d['error']]
    if 'training_seconds' in d:
        lines+=['',f"Training: {d['training_seconds']:.2f} seconds; peak reserved memory: {d['max_reserved_gib']:.2f} GiB."]
        lines+=['',f"Processed {d['training_examples']} protein examples and {d['padded_residue_examples']} padded residue examples: {d['examples_per_training_second']:.2f} examples/s and {d['padded_residues_per_training_second']:.2f} padded residues/s. Compare batch/length distributions before interpreting throughput differences."]
        h=d.get('hardware',{})
        if 'collection_mean_percent' in h:
            lines+=['',f"SM issue: {h['collection_mean_percent'].get('SM Issue [Throughput %]')}% within measured collection ranges; {h['whole_capture_mean_percent'].get('SM Issue [Throughput %]')}% over the entire capture. For full runs collection ranges include evaluation. Short-profile startup is not amortized."]
    if d['target_estimator']=='posterior':
        lines+=['',f"Target estimator: posterior mean plus detached conditional variance. Logged mean variance: {d.get('logged_posterior_variance_mean')}; logged mean variance/loss fraction: {d.get('logged_posterior_floor_fraction')}. These sparse logs are diagnostic, not an estimate of gradient-variance reduction. Time-bin errors still use sampled-label targets."]
    if 'training_subset' in d:
        subset=d['training_subset'];lines+=['',f"Tail adaptation: last {subset['tail_blocks']} blocks and output layers; {subset['trainable_parameters']:,}/{subset['total_parameters']:,} trainable parameters. Frozen raw and EMA parameters unchanged: {subset['frozen_unchanged']}."]
    if 'local_geometry' in d:
        aux=d['local_geometry'];lines+=['',f"Direct local-geometry objective: {aux['active_updates']}/{aux['updates']} updates had eligible late-time examples; {aux['positive_gradient_updates']} had positive auxiliary gradients. Maximum auxiliary/flow gradient norm ratio {aux['maximum_aux_to_flow_ratio']:.6f}; active buckets {aux['active_buckets']}. Mean logged geometry loss {aux['mean_geometry_loss']:.6f}. These are optimization diagnostics, not inference-quality evidence."]
    lines+=['','This is a training-capacity experiment. No model promotion or unseen-family accuracy claim is possible from these scores.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
