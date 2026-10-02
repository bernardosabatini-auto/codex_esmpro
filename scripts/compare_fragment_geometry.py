"""Audit matched fragment conditioning and decoded-objective learning traces."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from summarize_fragment_training import interval
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--objective',action='store_true');a=p.parse_args();runs=[a.baseline,a.candidate];ms=[json.loads((r/'manifest.json').read_text()) for r in runs];base,new=ms;configs=[m['config'] for m in ms]
    if any(m['status']!='complete' or m['updates']!=2000 or m['config']['arm'] not in ('adapter_only','full') for m in ms) or configs[1].get('variant')!='geometry' or (configs[0].get('variant')!='geometry' if a.objective else configs[0].get('variant') is not None):raise ValueError('Wrong completed arms')
    if a.objective and (not configs[1].get('auxiliary_motif') or configs[0].get('auxiliary_motif') or configs[0].get('distance_precision')!=configs[1].get('distance_precision')):raise ValueError('Wrong objective contrast')
    keys=('arm','protocol_sha256','seed','updates','batches','evaluation_steps','data_report_sha256','data_manifest_sha256','fragments_sha256','checkpoint_sha256','decoder_checkpoint_sha256','initial_manifest_sha256','initial_predictions_sha256')
    if any(configs[0][k]!=configs[1][k] for k in keys) or base['frozen_initial']!=new['frozen_initial'] or base['adapter_initial']!=(new['adapter_initial'] if a.objective else new['token_adapter_initial']):raise ValueError('Recipe/initial weight mismatch')
    trace=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    if len(base['training'])!=2000 or len(new['training'])!=2000:raise ValueError('Incomplete trace')
    for x,y in zip(base['training'],new['training']):
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
    for step in (500,2000):
        es=[next(e['scores'] for e in m['evaluations'] if e['step']==step) for m in ms]
        for cohort in ('train','development'):
            families=sorted({r['family'] for r in es[0] if r['cohort']==cohort})
            for metric in ('joint','motif_drms','coarse_valid','ca_lddt'):
                def value(r):return float(r['coarse_valid'] and r['motif_drms']<=1) if metric=='joint' else r[metric]
                values=[[np.mean([value(r) for r in e if (r['cohort'],r['mode'],r['family'])==(cohort,'conditioned',family)]) for family in families] for e in es];comparisons.append(dict(step=step,cohort=cohort,metric=metric,baseline=float(np.mean(values[0])),candidate=float(np.mean(values[1])),candidate_minus_baseline=interval(np.asarray(values[1])-np.asarray(values[0]))))
    d=dict(status='complete',contrast='decoded_motif_objective' if a.objective else 'direct_distance_input',matched_updates=2000,identical_initial_samples=initial_equal,source_manifest_hashes=[sha(r/'manifest.json') for r in runs],comparisons=comparisons);
    if a.objective:
        training=next(r for r in comparisons if r['step']==2000 and r['cohort']=='train' and r['metric']=='joint');validity=next(r for r in comparisons if r['step']==2000 and r['cohort']=='development' and r['metric']=='coarse_valid');d['objective_gate_passed']=training['candidate_minus_baseline']['ci95'][0]>0 and validity['candidate_minus_baseline']['ci95'][0]>=-.05
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Direct fragment-distance conditioning\n\nSame frozen generator, token-adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases or decoded motif supervision; every output retained.500diagnostic,2000primary. Training capacity is not designability or generalization.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
