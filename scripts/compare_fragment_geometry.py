"""Require matched token-only versus token-plus-distance learning traces."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from summarize_fragment_training import interval
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();runs=[a.baseline,a.candidate];ms=[json.loads((r/'manifest.json').read_text()) for r in runs];base,new=ms;configs=[m['config'] for m in ms]
    if any(m['status']!='complete' or m['updates']!=2000 or m['config']['arm']!='adapter_only' for m in ms) or configs[1].get('variant')!='geometry' or configs[0].get('variant') is not None:raise ValueError('Wrong completed arms')
    keys=('protocol_sha256','seed','updates','batches','evaluation_steps','data_report_sha256','data_manifest_sha256','fragments_sha256','checkpoint_sha256','decoder_checkpoint_sha256','initial_manifest_sha256','initial_predictions_sha256')
    if any(configs[0][k]!=configs[1][k] for k in keys) or base['frozen_initial']!=new['frozen_initial'] or base['adapter_initial']!=new['token_adapter_initial']:raise ValueError('Recipe/initial weight mismatch')
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
                values=[[np.mean([value(r) for r in e if (r['cohort'],r['mode'],r['family'])==(cohort,'conditioned',family)]) for family in families] for e in es];comparisons.append(dict(step=step,cohort=cohort,metric=metric,baseline=float(np.mean(values[0])),geometry=float(np.mean(values[1])),geometry_minus_baseline=interval(np.asarray(values[1])-np.asarray(values[0]))))
    d=dict(status='complete',matched_updates=2000,identical_initial_samples=initial_equal,source_manifest_hashes=[sha(r/'manifest.json') for r in runs],comparisons=comparisons);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Direct fragment-distance conditioning\n\nSame frozen generator, token-adapter initialization, data draws and training schedule. Candidate adds supplied intramotif distance biases; every output retained.500diagnostic,2000primary. Training capacity is not designability or generalization.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
