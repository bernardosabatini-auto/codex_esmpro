"""Audit paired training draws and compare the two prespecified fragment arms."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from summarize_fragment_training import interval
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();manifests=[json.loads((run/'manifest.json').read_text()) for run in a.runs];arms=[m['config']['arm'] for m in manifests]
    if arms!=['adapter_only','full']:raise ValueError('Supply adapter_only,full in order')
    ignore={'arm'};configs=[{k:v for k,v in m['config'].items() if k not in ignore} for m in manifests]
    if configs[0]!=configs[1] or any(m['updates']<a.step for m in manifests) or manifests[0]['adapter_initial']!=manifests[1]['adapter_initial']:raise ValueError('Unmatched recipe/initialization/incomplete')
    if manifests[0]['config']['profile_only']:raise ValueError('Full matched arms required')
    keys=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    for left,right in zip(*(m['training'][:a.step] for m in manifests)):
        if any(left[k]!=right[k] for k in keys):raise ValueError('Training draw mismatch at '+str(left['step']))
    initial_equal=0
    with h5py.File(a.runs[0]/'evaluation_0.h5') as left,h5py.File(a.runs[1]/'evaluation_0.h5') as right:
        for cohort in ('train','development'):
            for mode in ('conditioned','null'):
                if set(left[cohort+'/'+mode])!=set(right[cohort+'/'+mode]):raise ValueError('Initial inventory mismatch')
                for ident in left[cohort+'/'+mode]:
                    for key in ('latent','backbone'):
                        path=f'{cohort}/{mode}/{ident}/{key}'
                        if not np.array_equal(left[path][:],right[path][:]):raise ValueError('Initial predictions differ')
                    initial_equal+=4
    evaluations=[next(e for e in m['evaluations'] if e['step']==a.step)['scores'] for m in manifests];records=[]
    for cohort in ('train','development'):
        families=sorted({r['family'] for r in evaluations[0] if r['cohort']==cohort})
        for metric in ('coarse_valid','motif_drms','ca_lddt','joint'):
            def value(row):return float(row['coarse_valid'] and row['motif_drms']<=1) if metric=='joint' else row[metric]
            for mode in ('conditioned','null'):
                averages=[[float(np.mean([value(r) for r in rows if (r['cohort'],r['family'],r['mode'])==(cohort,family,mode)])) for family in families] for rows in evaluations];records.append(dict(cohort=cohort,mode=mode,metric=metric,adapter_only=float(np.mean(averages[0])),full=float(np.mean(averages[1])),full_minus_adapter=interval(np.array(averages[1])-np.array(averages[0]))))
    d=dict(status='complete',step=a.step,diagnostic_only=a.step!=2000,matched_updates=a.step,identical_initial_samples=initial_equal,source_manifest_hashes=[sha(run/'manifest.json') for run in a.runs],comparisons=records);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Matched fragment-conditioning arms\n\nIdentical training draws, fragment choices, flow noise/time/dropout/history and initial outputs.500is diagnostic;2000is the prespecified capacity endpoint. Raw motif/geometry scores do not establish designability.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
