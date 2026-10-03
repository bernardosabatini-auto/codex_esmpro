"""Evidence-bound replacement of a failed numerical assay, without more designs."""
import json
from pathlib import Path
from prepare_overfit import sha


def audit_recovery(config):
    recovery=config.get('numerical_recovery')
    if recovery is None:return None
    if config.get('assay')!='extra_fragment_refold':raise ValueError('Recovery scope changed')
    for key in ('failed_manifest','failed_refolded','probe_manifest','probe_report'):
        if sha(recovery[key])!=recovery[key+'_sha256']:raise ValueError('Changed recovery evidence: '+key)
    old=json.loads(Path(recovery['failed_manifest']).read_text())
    probe=json.loads(Path(recovery['probe_manifest']).read_text())
    report=json.loads(Path(recovery['probe_report']).read_text())
    if old['status']!='failed' or old['error']!='ValueError: Teacher repeatability failed' or len(old['records'])!=1:
        raise ValueError('Not the declared first-refold numerical failure')
    if old['config']!={k:v for k,v in config.items() if k!='numerical_recovery'}:
        raise ValueError('Changed recovery assay or sequence budget')
    from summarize_teacher_repeatability_probe import analyze
    if report!={**analyze(probe),'manifest_sha256':sha(recovery['probe_manifest'])}:
        raise ValueError('Unaudited deterministic probe')
    if report['status']!='complete' or not report['deterministic_algorithms'] or report['failed_pairs'] or report['feature_mutations'] or report['feature_rng_changes'] or not report['fresh_feature_hashes_match']:
        raise ValueError('Unqualified deterministic execution')
    if probe['config']['failed_manifest_sha256']!=recovery['failed_manifest_sha256'] or probe['config']['failed_refolded_sha256']!=recovery['failed_refolded_sha256']:
        raise ValueError('Unmatched failed probe source')
    if any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in report['original_comparisons']):
        raise ValueError('Deterministic execution differs from original output')
    return old
