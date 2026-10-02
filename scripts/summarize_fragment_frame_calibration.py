"""Audit paired reconstruction errors without changing the failed data gate."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from calibrate_fragment_frame import scores
from prepare_overfit import sha
from summarize_fragment_training import interval


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config']
    for key in ('protocol','data_manifest','data_report','fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed calibration source')
    if sha(run/'reconstructions.h5')!=m['predictions_sha256']:raise ValueError('Changed predictions')
    rows={(r['target_id'],r['condition']):r for r in m['records']}
    with h5py.File(c['fragments']) as src,h5py.File(run/'reconstructions.h5') as pred:
        wanted={(i,k) for i,g in src['train'].items() for k in g['conditions']}
        if len(rows)!=288 or len(m['records'])!=288 or set(rows)!=wanted:raise ValueError('Incomplete calibration')
        for ident,condition in sorted(wanted):
            g=src['train/'+ident];q=g['conditions/'+condition];args=(g['reference_backbone'][:],q['fragment'][:],int(q.attrs['start']))
            for arm,bb in [('original',pred[ident+'/'+condition][:]),('anchored',q['target_roundtrip'][:])]:
                actual=scores(bb,*args)
                if any(not np.isfinite(v) or abs(v-rows[ident,condition][arm][k])>1e-6 for k,v in actual.items()):raise ValueError('Reconstruction score mismatch')
    values=list(rows.values());summary={}
    for arm in ('original','anchored'):
        summary[arm]=dict(coarse_valid=sum(r[arm]['coarse_valid'] for r in values),valid_global_under_half_A=sum(r[arm]['coarse_valid'] and r[arm]['global_rmsd']<=.5 for r in values),valid_motif_under_one_A=sum(r[arm]['coarse_valid'] and r[arm]['motif_rmsd']<=1 for r in values),mean_global_rmsd=float(np.mean([r[arm]['global_rmsd'] for r in values])),mean_motif_rmsd=float(np.mean([r[arm]['motif_rmsd'] for r in values])))
    differences={key:interval([np.mean([r['anchored'][key]-r['original'][key] for r in values if r['target_id']==ident]) for ident in sorted({r['target_id'] for r in values})]) for key in ('global_rmsd','motif_rmsd')}
    return dict(status='complete',manifest_sha256=sha(path),paired_cases=288,training_families=32,summary=summary,anchored_minus_original=differences,original_data_gate_passed=json.loads(Path(c['data_report']).read_text())['training_gate_passed'],interpretation='Diagnostic only; original failed gate preserved; no training authorized by this report',elapsed_seconds=m['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Original versus anchored reconstruction calibration\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')


if __name__=='__main__':main()
