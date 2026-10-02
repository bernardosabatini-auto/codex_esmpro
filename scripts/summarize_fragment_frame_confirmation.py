"""Audit all fresh-noise pairs; preserve the original failed absolute gate."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from calibrate_fragment_frame import scores
from prepare_overfit import sha
from summarize_fragment_training import interval


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),relative_label_gate_passed=False)
    c=m['config']
    for key in ('protocol','data_manifest','data_report','calibration_report','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed confirmation source')
    protocol=json.loads(Path(c['protocol']).read_text());seeds=protocol['seeds']
    if c['seeds']!=seeds or sha(run/'reconstructions.h5')!=m['predictions_sha256']:raise ValueError('Changed predictions/seeds')
    index={(r['target_id'],r['condition'],r['seed']):r for r in m['records']}
    with h5py.File(c['fragments']) as src,h5py.File(run/'reconstructions.h5') as pred:
        wanted={(i,k,s) for i,g in src['train'].items() for k in g['conditions'] for s in seeds}
        if len(index)!=864 or len(m['records'])!=864 or set(index)!=wanted:raise ValueError('Incomplete confirmation')
        for ident,condition,seed in sorted(wanted):
            g=src['train/'+ident];q=g['conditions/'+condition];args=(g['reference_backbone'][:],q['fragment'][:],int(q.attrs['start']))
            for arm in ('original','anchored'):
                actual=scores(pred[f'{ident}/{condition}/{seed}/{arm}'][:],*args)
                if any(not np.isfinite(v) or abs(v-index[ident,condition,seed][arm][k])>1e-6 for k,v in actual.items()):raise ValueError('Confirmation score mismatch')
    rows=list(index.values());summary={}
    for arm in ('original','anchored'):
        summary[arm]=dict(coarse_valid_fraction=float(np.mean([r[arm]['coarse_valid'] for r in rows])),valid_motif_under_one_A_fraction=float(np.mean([r[arm]['coarse_valid'] and r[arm]['motif_rmsd']<=1 for r in rows])),valid_global_under_half_A_fraction=float(np.mean([r[arm]['coarse_valid'] and r[arm]['global_rmsd']<=.5 for r in rows])))
    delta={k:interval([np.mean([r['anchored'][k]-r['original'][k] for r in rows if r['target_id']==i]) for i in sorted({r['target_id'] for r in rows})]) for k in ('global_rmsd','motif_rmsd')}
    limits=protocol['limits'];gate=all(v['ci95'][1]<=limits['maximum_error_increase_A'] for v in delta.values()) and all(s['coarse_valid_fraction']>=limits['minimum_valid_fraction'] and s['valid_motif_under_one_A_fraction']>=limits['minimum_motif_fraction'] for s in summary.values()) and summary['anchored']['valid_global_under_half_A_fraction']>=summary['original']['valid_global_under_half_A_fraction']-limits['maximum_global_pass_fraction_loss']
    return dict(status='complete',manifest_sha256=sha(path),data_manifest_sha256=c['data_manifest_sha256'],fragments_sha256=c['fragments_sha256'],paired_cases=864,training_families=32,summary=summary,anchored_minus_original=delta,relative_label_gate_passed=gate,original_absolute_gate_passed=json.loads(Path(c['data_report']).read_text())['training_gate_passed'],interpretation='Revised baseline-relative label-quality screen; three fresh decoder seeds on the same32trainingfamilies, not independent structural validation. Original failed absolute gate preserved. No model performance claim.',elapsed_seconds=m['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fresh-noise target frame confirmation\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')


if __name__=='__main__':main()
