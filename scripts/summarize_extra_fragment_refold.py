"""Retained constraints and global/scaffold agreement must share one valid refold."""
import argparse,itertools,json
from pathlib import Path
import h5py,numpy as np
from fragment_refinement_core import score_assay
from latentfold.fragment_designability import scaffold_rmsd
from latentfold.metrics import usalign_coordinates
from prepare_extra_fragment_refold import audit_inputs
from prepare_overfit import sha


def same_scaffold_success(primary_indices,scaffold_scores):
    if len(scaffold_scores)!=8 or not np.isfinite(scaffold_scores).all():raise ValueError('Eight finite scaffold scores required')
    return [k for k in primary_indices if scaffold_scores[k]>.5]


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];audit_inputs(c);records=score_assay(run);diversity=[]
    if c.get('teacher_deterministic_algorithms') and m.get('teacher_deterministic_algorithms') is not True:raise ValueError('Declared deterministic teacher execution missing')
    if c.get('numerical_recovery'):
        from teacher_numerical_recovery import audit_recovery
        original=audit_recovery(c);control=m['recovery_control']
        if m['sequences']!=original['sequences'] or control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Recovery sequence or numerical parity failed')
    with h5py.File(run/'refolded.h5') as folds,h5py.File(c['predictions']) as raw:
        for r in records:
            bb=raw[r['dataset']][0];fragment=raw['motifs/'+r['target_id']][:];mask=np.ones(len(bb),bool);mask[r['motif_start']:r['motif_start']+len(fragment)]=False
            scores=[usalign_coordinates(c['usalign'],folds[r['name']+'/'+str(k)][:][mask,1],bb[mask,1]) for k in range(8)]
            good=same_scaffold_success(r['successful_refold_indices'] if r['raw_gate_passed'] else [],scores)
            r.update(scaffold_scores=scores,scaffold_joint_success=bool(good),scaffold_successful_refold_indices=good)
        for arm,ident in sorted({(r['arm'],r['target_id']) for r in records if r['scaffold_joint_success'] and r['arm']!='native'}):
            rr=sorted([r for r in records if r['arm']==arm and r['target_id']==ident and r['scaffold_joint_success']],key=lambda r:r['generation_slot']);pairs=[]
            for l,r in itertools.combinations(rr,2):
                li=l['scaffold_successful_refold_indices'][0];ri=r['scaffold_successful_refold_indices'][0];x=folds[l['name']+'/'+str(li)][:];y=folds[r['name']+'/'+str(ri)][:];mask=np.zeros(len(x),bool);mask[l['motif_start']:l['motif_start']+len(raw['motifs/'+ident])]=True
                pairs.append(dict(left_slot=l['generation_slot'],right_slot=r['generation_slot'],left_sequence=li,right_sequence=ri,global_tm=usalign_coordinates(c['usalign'],x[:,1],y[:,1]),scaffold_tm=usalign_coordinates(c['usalign'],x[~mask,1],y[~mask,1]),motif_aligned_scaffold_rmsd=scaffold_rmsd(x,y,mask)))
            diversity.append(dict(arm=arm,target_id=ident,successful_backbones=len(rr),pairs=pairs))
    native={r['target_id']:{k:r[k] for k in ('strict_joint_success','scaffold_joint_success','valid_designable')} for r in records if r['arm']=='native'}
    if c.get('native_reuse'):
        source=c['native_reuse'];native=json.loads(Path(source['report']).read_text())['native_controls']
    result=dict(status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),generation_inventory_sha256=c['generation_manifest_sha256'],partition=c['partition'],target_ids=c['target_ids'],screen_rows=c['screen_rows'],records=records,completed_refolds=len(m['records']),native_controls=native,successful_scaffold_diversity=diversity,elapsed_seconds=m['elapsed_seconds'],scope='Disjoint16-family partition; eight fixed-motif designs per selected backbone. Primary and stronger scaffold success require the same valid refold. All raw failures remain in the generation denominator. Diversity is across scaffold designs, potentially with different full sequences.')
    if c.get('native_reuse'):result['reused_native_source']=c['native_reuse']
    if c.get('numerical_recovery'):result['numerical_recovery']=dict(evidence=c['numerical_recovery'],original_output_parity=m['recovery_control'],policy='Deterministic algorithms; identical eight sequences and seeds; failed run excluded, not pooled.')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k not in ('records','screen_rows')};a.output.with_suffix('.md').write_text('# Additional-family same-refold assay\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')

if __name__=='__main__':main()
