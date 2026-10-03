"""Same-refold scoring of every training-only preference candidate."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np

from fragment_refinement_core import score_assay
from latentfold.metrics import usalign_coordinates
from latentfold.fragment_preferences import split_preference
from prepare_fragment_preference_refold import audit_inputs
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];gc,spec=audit_inputs(c)
    if not m['teacher_deterministic_algorithms']:raise ValueError('Teacher execution policy not applied')
    records=score_assay(run)
    with h5py.File(c['predictions']) as raw,h5py.File(run/'refolded.h5') as folded:
        for r in records:
            bb=raw[r['dataset']][0];mask=np.ones(r['length'],bool)
            mask[r['motif_start']:r['motif_start']+len(r['fixed_sequence'])]=False
            for k,row in enumerate(r['refolds']):
                row['scaffold_tm']=usalign_coordinates(c['usalign'],folded[r['name']+'/'+str(k)][:][mask,1],bb[mask,1])
            passing=[k for k in r['successful_refold_indices'] if r['refolds'][k]['scaffold_tm']>.5] if r['raw_gate_passed'] else []
            r.update(scaffold_successful_refold_indices=passing,scaffold_joint_success=bool(passing))
    params={k:spec['preference'][k] for k in ('minimum_quality','discovery_margin','confirmation_margin')}
    prefs=[split_preference([dict(r,slot=r['generation_slot']) for r in records if r['target_id']==ident],**params)
           for ident in sorted({r['target_id'] for r in records})]
    return dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),
                generation_manifest_sha256=c['generation_manifest_sha256'],protocol_sha256=c['protocol_sha256'],
                partition=c['partition'],completed_refolds=len(m['records']),records=records,preferences=prefs,
                raw_matches=sum(r['raw_gate_passed'] for r in records),strong=sum(r['scaffold_joint_success'] for r in records),
                designable=sum(r['valid_designable'] for r in records),eligible=sum(r['eligible'] for r in prefs),
                confirmed=sum(r['confirmed'] for r in prefs),elapsed_seconds=m['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Training-only preference calibration partition\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('records','preferences')},indent=2)+'\n```\n')


if __name__=='__main__':main()
