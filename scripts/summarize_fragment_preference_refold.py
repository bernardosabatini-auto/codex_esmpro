"""Same-refold scoring of every training-only preference candidate."""
import argparse
import fcntl
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
        if gc.get('torsion_closure_refold'):
            from fragment_junction_core import flank_bonds
            from latentfold.connected_refold import connected_outcome
            if m.get('cpu_preflight_file_identity_unchanged') is not True:raise ValueError('Missing post-worker input identity audit')
            generation=json.loads(Path(c['generation_report']).read_text())
            physical={(r['target_id'],r['generation_slot']):r['refold_eligible_geometry'] for r in generation['records'] if r['arm']=='generated_cond'}
            for r in records:
                for k,row in enumerate(r['refolds']):
                    edges=flank_bonds(folded[r['name']+'/'+str(k)][:],r['motif_start'],len(r['fixed_sequence']),8)
                    row['flank_edges_valid']=edges['all_edges_valid']
                r.update(connected_outcome(r['raw'],r['refolds'],physical_raw=physical[r['target_id'],r['generation_slot']]))
    skip_preferences=spec.get('repaint_student_model_validation') or gc.get('torsion_closure_refold') or gc.get('oracle_teacher_refold') or spec.get('native_anchor_model_validation') or gc.get('native_positive_coverage') or gc.get('pretrained_masked_refold') or gc.get('scaffold_clock_refold') or gc.get('fragment_decoder_refold') or gc.get('fragment_decoder_fm_refold') or gc.get('fragment_inpainting_refold')
    params={} if skip_preferences else {k:spec['preference'][k] for k in ('minimum_quality','discovery_margin','confirmation_margin')}
    if skip_preferences:
        prefs=[]
    elif spec.get('native_anchor_calibration'):
        from native_anchor_calibration import native_pair
        generation=json.loads(Path(c['generation_report']).read_text())
        for r in records:
            if r['arm']=='native_latent':
                original=next(x for x in generation['native_records'] if (x['target_id'],x['generation_slot'])==(r['target_id'],r['generation_slot']))
                r['full_native_ca_rmsd']=original['full_native_ca_rmsd']
        prefs=[native_pair(sorted([r for r in records if r['target_id']==ident and r['arm']=='native_latent'],key=lambda r:r['generation_slot']),
                           [r for r in records if r['target_id']==ident and r['arm']=='parent6000'],**params)
               for ident in sorted({r['target_id'] for r in records})]
    else:
        prefs=[split_preference([dict(r,slot=r['generation_slot']) for r in records if r['target_id']==ident],**params)
               for ident in sorted({r['target_id'] for r in records})]
    result=dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),
                generation_manifest_sha256=c['generation_manifest_sha256'],protocol_sha256=c['protocol_sha256'],
                partition=c['partition'],completed_refolds=len(m['records']),records=records,preferences=prefs,
                raw_matches=sum(r['raw_gate_passed'] for r in records),strong=sum(r['scaffold_joint_success'] for r in records),
                designable=sum(r['valid_designable'] for r in records),eligible=sum(r['eligible'] for r in prefs),
                confirmed=sum(r['confirmed'] for r in prefs),elapsed_seconds=m['elapsed_seconds'])
    if spec.get('native_anchor_calibration'):
        result.update(native_anchor_calibration=True,summary=[dict(arm=arm,samples=sum(r['arm']==arm for r in records),strong=sum(r['arm']==arm and r['scaffold_joint_success'] for r in records),designable=sum(r['arm']==arm and r['valid_designable'] for r in records)) for arm in ('parent6000','native_latent')])
    if gc.get('native_positive_coverage'):
        result['native_positive_coverage']=True;result.pop('eligible');result.pop('confirmed')
    if gc.get('pretrained_masked_refold'):
        result.update(pretrained_masked_refold=True,arm=gc['arm'])
    if gc.get('scaffold_clock_refold'):
        result.update(scaffold_clock_refold=True,arm=gc['arm'])
    if gc.get('fragment_decoder_refold'):
        result.update(fragment_decoder_refold=True,arm=gc['arm'])
    if gc.get('fragment_decoder_fm_refold'):
        result.update(fragment_decoder_fm_refold=True,arm=gc['arm'])
    if gc.get('oracle_teacher_refold'):
        result.update(oracle_teacher_refold=True,arm=gc['arm'])
    if gc.get('fragment_inpainting_refold'):result.update(fragment_inpainting_refold=True,arm=gc['arm'])
    if gc.get('torsion_closure_refold'):
        result.update(torsion_closure_refold=True,arm=gc['arm'],
            complete_strict=sum(r['complete_strict'] for r in records),
            connected_designable=sum(r['connected_designable'] for r in records),
            complete_connected_designable=sum(r['complete_connected_designable'] for r in records))
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    # Allow independent CPU audits of disjoint completed GPU partitions. The
    # watcher may join the same audit; a lock prevents duplicate scoring.
    with a.output.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        target=a.output.with_suffix('.json')
        if target.exists() and a.output.with_suffix('.md').exists():
            old=json.loads(target.read_text());run=a.runs[0]
            if (old['status']=='complete' and old['manifest_sha256']==sha(run/'manifest.json')
                    and old['refolded_sha256']==sha(run/'refolded.h5')):return
        d=analyze(a.runs[0]);temporary=target.with_suffix('.json.tmp');temporary.write_text(json.dumps(d,indent=2)+'\n');temporary.replace(target)
        title='Native-positive qualification partition' if d.get('native_positive_coverage') else 'Training-only preference calibration partition'
        if d.get('pretrained_masked_refold'):title='Pretrained masked-flow refolding'
        if d.get('scaffold_clock_refold'):title='Whole-chain scaffold-clock refolding'
        if d.get('fragment_decoder_refold'):title='Fragment-conditioned coordinate-decoder refolding'
        if d.get('oracle_teacher_refold'):title='Oracle RePaint teacher fixed-motif refolds'
        if d.get('fragment_decoder_fm_refold'):title='Full fragment-conditioned decoder denoising refolds'
        if d.get('fragment_inpainting_refold'):title='Fixed-fragment coordinate-inpainting refolds'
        if d.get('torsion_closure_refold'):title='Constructive torsion-closure same-refold designability'
        a.output.with_suffix('.md').write_text('# '+title+'\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k not in ('records','preferences')},indent=2)+'\n```\n')


if __name__=='__main__':main()
