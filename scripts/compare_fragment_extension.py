"""Compare matched exposure while preserving each arm's distinct trained parent."""
import argparse,json
from pathlib import Path
import numpy as np
from fragment_extension import audit_extension
from prepare_overfit import sha
from summarize_fragment_training import interval

TRACE=('step','length','batch','ids','conditions','learning_rate_factor','self_conditioned','noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')


def matched_traces(left,right):
    if len(left)!=2000 or len(right)!=2000 or any(any(x[k]!=y[k] for k in TRACE) for x,y in zip(left,right)):
        raise ValueError('Unmatched primary training exposure')


def main():
    p=argparse.ArgumentParser();p.add_argument('--plain',type=Path,required=True);p.add_argument('--weighted',type=Path,required=True);p.add_argument('--strict-report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    runs=[a.plain.resolve(),a.weighted.resolve()];ms=[];parents=[]
    for arm,run in zip(('plain','weighted'),runs):
        m=json.loads((run/'manifest.json').read_text());c=m['config'];audit_extension(c)
        report_path=root/'reports'/(run.name+'.json');report=json.loads(report_path.read_text())
        if m['status']!='complete' or m['updates']!=2000 or c['profile_only'] or c['extension_arm']!=arm or report['status']!='complete' or report['manifest_sha256']!=sha(run/'manifest.json') or report['total_training_updates']!=6000:raise ValueError('Incomplete matched extension')
        if len(m['warm_controls'])!=384 or any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in m['warm_controls']):raise ValueError('Own-parent initialization changed')
        ms.append(m);parents.append(Path(c['warm_parent_manifest']).parent)
    keys=('seed','updates','evaluation_steps','batches','fragments_sha256','initial_predictions_sha256','decoder_checkpoint_sha256','extension_protocol_sha256','total_prior_updates')
    if any(ms[0]['config'][k]!=ms[1]['config'][k] for k in keys):raise ValueError('Different continuation recipes')
    matched_traces(ms[0]['training'],ms[1]['training'])
    pm=[json.loads((r/'manifest.json').read_text()) for r in parents];matched_traces(pm[0]['training'],pm[1]['training'])
    prior=json.loads((root/'reports/fragment_latent_weight_comparison_50019364.json').read_text())
    if prior['status']!='complete' or prior['matched_updates']!=2000 or prior['identical_initial_samples']!=384 or prior['source_manifest_hashes']!=[sha(r/'manifest.json') for r in parents]:raise ValueError('Original paired contrast no longer audited')
    strict=json.loads(a.strict_report.read_text());expected={r.name for r in parents+runs}
    if strict['status']!='complete' or {Path(s['run']).name for s in strict['sources']}!=expected:raise ValueError('Missing strict source')
    for r in parents+runs:
        source=next(s for s in strict['sources'] if Path(s['run']).name==r.name)
        if source['manifest_sha256']!=sha(r/'manifest.json') or source['predictions_sha256']!=sha(r/'evaluation_2000.h5'):raise ValueError('Changed strict source')
    records=strict['records'];comparisons=[]
    for cohort in ('train','development'):
        for metric in ('strict_raw','motif_ca_rmsd','coarse_valid'):
            families=sorted({r['family'] for r in records if r['cohort']==cohort})
            def values(run):return np.array([np.mean([r[metric] for r in records if r['run']==run.name and r['cohort']==cohort and r['mode']=='conditioned' and r['family']==f]) for f in families])
            old=[values(r) for r in parents];new=[values(r) for r in runs]
            comparisons.append(dict(cohort=cohort,metric=metric,plain_parent=float(old[0].mean()),weighted_parent=float(old[1].mean()),plain_extended=float(new[0].mean()),weighted_extended=float(new[1].mean()),extended_weighted_minus_plain=interval(new[1]-new[0]),plain_extension_change=interval(new[0]-old[0]),weighted_extension_change=interval(new[1]-old[1])))
    d=dict(status='complete',additional_matched_updates=2000,total_updates_per_arm=6000,original_pair_matched=True,own_parent_initial_outputs_per_arm=384,initial_outputs_identical_between_extension_arms=False,comparisons=comparisons,source_manifest_hashes=[sha(r/'manifest.json') for r in parents+runs],strict_report_sha256=sha(a.strict_report),interpretation='Fixed development/capacity panels, distinct trained parents and matched continuation exposure. Strict raw retention is not designability. Each final model receives the unchanged same-refold assay; no locked-test claim.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Matched conditioning duration test\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
