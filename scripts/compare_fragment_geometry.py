"""Audit matched fragment conditioning and decoded-objective learning traces."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from summarize_fragment_training import interval
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--step',type=int,choices=[500,2000],default=2000);mode=p.add_mutually_exclusive_group();mode.add_argument('--objective',action='store_true');mode.add_argument('--trunk',action='store_true');mode.add_argument('--data-breadth',action='store_true');mode.add_argument('--rollout-objective',action='store_true');mode.add_argument('--target-frame',action='store_true');mode.add_argument('--representation',action='store_true');mode.add_argument('--backbone-tokens',action='store_true');mode.add_argument('--latent-weight',action='store_true');a=p.parse_args();runs=[a.baseline,a.candidate];ms=[json.loads((r/'manifest.json').read_text()) for r in runs];base,new=ms;configs=[m['config'] for m in ms]
    if any(m['status']!='complete' or m['updates']!=m['config']['updates'] or m['config']['profile_only'] or a.step not in m['config']['evaluation_steps'] or m['config']['arm'] not in ('adapter_only','full') for m in ms) or configs[1].get('variant')!='geometry' or (configs[0].get('variant')!='geometry' if a.objective or a.trunk or a.data_breadth or a.rollout_objective or a.target_frame or a.representation or a.backbone_tokens or a.latent_weight else configs[0].get('variant') is not None):raise ValueError('Wrong completed arms')
    if a.objective and (not configs[1].get('auxiliary_motif') or configs[0].get('auxiliary_motif') or configs[0].get('distance_precision')!=configs[1].get('distance_precision')):raise ValueError('Wrong objective contrast')
    if a.trunk and ([c['arm'] for c in configs]!=['adapter_only','full'] or any(c.get('auxiliary_motif') for c in configs) or configs[0].get('distance_precision')!=configs[1].get('distance_precision')):raise ValueError('Wrong trunk contrast')
    if a.data_breadth and (any(c['arm']!='full' or not c.get('warm_start') or c.get('auxiliary_motif') or c.get('rollout_motif') or c.get('target_frame_training') for c in configs) or not configs[1].get('expanded_fragment_data') or configs[0].get('training_protein_count',128 if configs[0].get('expanded_fragment_data') else 32)>=configs[1].get('training_protein_count',128)):raise ValueError('Wrong data-breadth contrast')
    if a.rollout_objective and (any(c['arm']!='full' or not c.get('warm_start') or c.get('auxiliary_motif') for c in configs) or configs[0].get('rollout_motif') or not configs[1].get('rollout_motif')):raise ValueError('Wrong rollout objective contrast')
    if a.rollout_objective and (bool(configs[0].get('expanded_fragment_data'))!=bool(configs[1].get('expanded_fragment_data')) or configs[0].get('evaluation_train_ids')!=configs[1].get('evaluation_train_ids')):raise ValueError('Rollout comparison must match corpus')
    if a.target_frame and (any(c['arm']!='full' or not c.get('warm_start') or c.get('rollout_motif') or c.get('expanded_fragment_data') for c in configs) or configs[0].get('target_frame_training') or not configs[1].get('target_frame_training')):raise ValueError('Wrong target-frame contrast')
    if a.representation and (any(c['arm']!='full' or c.get('warm_start') or c.get('auxiliary_motif') or c.get('expanded_fragment_data') for c in configs) or configs[0].get('fragment_representation') or configs[1].get('fragment_representation')!='geometry_sequence'):raise ValueError('Wrong representation contrast')
    if a.backbone_tokens and (any(c['arm']!='full' or c.get('warm_start') or c.get('fragment_representation') for c in configs) or configs[0].get('backbone_tokens') or not configs[1].get('backbone_tokens')):raise ValueError('Wrong backbone-token contrast')
    if a.latent_weight and (any(c['arm']!='full' or not c.get('warm_start') or c.get('training_protein_count',128 if c.get('expanded_fragment_data') else 32)!=128 or c.get('rollout_motif') or c.get('backbone_tokens') or c.get('target_frame_training') for c in configs) or configs[0].get('latent_motif_weight') or configs[1].get('latent_motif_weight')!=3):raise ValueError('Wrong latent motif weight contrast')
    keys=('protocol_sha256','seed','updates','batches','evaluation_steps','data_report_sha256','data_manifest_sha256','fragments_sha256','checkpoint_sha256','decoder_checkpoint_sha256','initial_manifest_sha256','initial_predictions_sha256')
    if a.step==500:keys=tuple(k for k in keys if k not in ('updates','evaluation_steps'))
    if a.data_breadth:keys=tuple(k for k in keys if k not in ('data_report_sha256','data_manifest_sha256','fragments_sha256'))+('warm_protocol_sha256','warm_parent_manifest_sha256','warm_parent_report_sha256','warm_predictions_sha256')
    if a.target_frame:keys=tuple(k for k in keys if k!='fragments_sha256')
    if a.rollout_objective or a.target_frame:keys+=('warm_protocol_sha256','warm_parent_manifest_sha256','warm_parent_report_sha256','warm_predictions_sha256')
    if any(configs[0][k]!=configs[1][k] for k in keys) or (not a.trunk and (configs[0]['arm']!=configs[1]['arm'] or base['frozen_initial']!=new['frozen_initial'])) or base['adapter_initial']!=(new['shared_adapter_initial'] if a.backbone_tokens else new['adapter_initial'] if a.objective or a.trunk or a.data_breadth or a.rollout_objective or a.target_frame or a.representation or a.backbone_tokens or a.latent_weight else new['token_adapter_initial']):raise ValueError('Recipe/initial weight mismatch')
    trace=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    if a.data_breadth:trace=tuple(k for k in trace if k not in ('ids','conditions'))
    if len(base['training'])!=base['updates'] or len(new['training'])!=new['updates']:raise ValueError('Incomplete trace')
    for x,y in zip(base['training'][:a.step],new['training'][:a.step]):
        if any(x[k]!=y[k] for k in trace):raise ValueError('Training draw mismatch')
    initial_equal=0
    with h5py.File(a.baseline/'evaluation_0.h5') as left,h5py.File(a.candidate/'evaluation_0.h5') as right:
        for cohort in ('train','development'):
            for mode in ('conditioned','null'):
                if set(left[cohort+'/'+mode])!=set(right[cohort+'/'+mode]):raise ValueError('Initial inventory mismatch')
                for ident in left[cohort+'/'+mode]:
                    for key in ('latent','backbone'):
                        path=f'{cohort}/{mode}/{ident}/{key}'
                        if not np.array_equal(left[path][:],right[path][:]):raise ValueError('Initial outputs differ')
                    initial_equal+=4
    comparisons=[]
    for step in ([500] if a.step==500 else [500,2000]):
        es=[next(e['scores'] for e in m['evaluations'] if e['step']==step) for m in ms]
        for cohort in ('train','development'):
            families=sorted({r['family'] for r in es[0] if r['cohort']==cohort})
            for metric in ('joint','motif_drms','coarse_valid','ca_lddt'):
                def value(r):return float(r['coarse_valid'] and r['motif_drms']<=1) if metric=='joint' else r[metric]
                values=[[np.mean([value(r) for r in e if (r['cohort'],r['mode'],r['family'])==(cohort,'conditioned',family)]) for family in families] for e in es];comparisons.append(dict(step=step,cohort=cohort,metric=metric,baseline=float(np.mean(values[0])),candidate=float(np.mean(values[1])),candidate_minus_baseline=interval(np.asarray(values[1])-np.asarray(values[0]))))
    d=dict(status='complete',contrast='conditional_latent_motif_weight' if a.latent_weight else 'direct_backbone_token_input' if a.backbone_tokens else 'standalone_latent_input_ablation' if a.representation else 'conditional_target_frame' if a.target_frame else 'actual_rollout_motif_objective' if a.rollout_objective else 'decoded_motif_objective' if a.objective else 'reference_data_breadth' if a.data_breadth else 'trainable_trunk' if a.trunk else 'direct_distance_input',matched_updates=a.step,comparison_endpoint=a.step,target_draws_matched=not a.data_breadth,identical_initial_samples=initial_equal,source_manifest_hashes=[sha(r/'manifest.json') for r in runs],comparisons=comparisons);
    if a.objective:
        training=next(r for r in comparisons if r['step']==a.step and r['cohort']=='train' and r['metric']=='joint');validity=next(r for r in comparisons if r['step']==a.step and r['cohort']=='development' and r['metric']=='coarse_valid');d['objective_gate_passed']=training['candidate_minus_baseline']['ci95'][0]>0 and validity['candidate_minus_baseline']['ci95'][0]>=-.05
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fragment conditioning comparison\n\nSame original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
