"""Strict same-refold outcomes with every screened raw failure in the denominator."""
import argparse,json,itertools
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit,same_refold_success
from prepare_fragment_strict_followup import audit_inputs
from fixed_motif_design import verify_fixed_sequences
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config']
    if c.get('assay')=='fragment_repetition_refold':
        from prepare_fragment_repetition_refold import audit_inputs as audit_repetition
        audit_repetition(c,check_teacher=False)
    else:audit_inputs(c,check_teacher=False)
    verify_fixed_sequences(m['sequences'],c['entries']);index={(r['name'],r['sequence_index']):r for r in m['records']};wanted={(r['name'],k) for r in c['entries'] for k in range(8)}
    if len(index)!=len(m['records']) or set(index)!=wanted or m['training_updates_executed']:raise ValueError('Incomplete/changed refold inventory')
    natives={r['name'] for r in c['entries'] if r['arm']=='native'}
    if len(m['controls'])!=len(natives) or {r['name'] for r in m['controls']}!=natives or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Repeatability control failed')
    records=[]
    with h5py.File(c['predictions']) as rawfile,h5py.File(run/'refolded.h5') as refold:
        if set(refold)!={r['name'] for r in c['entries']}:raise ValueError('Extra refold groups')
        for r in c['entries']:
            name=r['name'];bb=rawfile[r['dataset']][0];fragment=rawfile['motifs/'+r['target_id']][:];raw=dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**motif_fit(bb,fragment,r['motif_start']));rows=[]
            if set(refold[name])!=set(map(str,range(8))):raise ValueError('Missing refold')
            for k in range(8):
                x=refold[name+'/'+str(k)][:]
                if x.shape!=bb.shape or not np.isfinite(x).all():raise ValueError('Invalid refold')
                tm=usalign_coordinates(c['usalign'],x[:,1],bb[:,1])
                if abs(tm-index[name,k]['sc_tm'])>1e-7:raise ValueError('Global score mismatch')
                rows.append(dict(sequence_index=k,sc_tm=tm,coarse_valid=bool(backbone_geometry(x[None])['coarse_valid'][0]),**motif_fit(x,fragment,r['motif_start'])))
            records.append(dict(**r,raw=raw,refolds=rows,**same_refold_success(raw,rows)))
    positive={r['target_id']:r['strict_joint_success'] for r in records if r['arm']=='native'};summaries=[]
    for s in c['screens']:
        arm=s['arm'];screen=[r for r in c['screen_rows'] if r['arm']==arm];rr=[r for r in records if r['arm']==arm];success=[r for r in rr if r['strict_joint_success']]
        summaries.append(dict(arm=arm,screened=len(screen),families=len({r['family'] for r in screen}),raw_matches=len(rr),known_raw_failures=len(screen)-len(rr),strict_same_refold_successes=len(success),strict_fraction=len(success)/len(screen),successful_families=len({r['family'] for r in success}),successes_with_passing_native_control=sum(positive[r['target_id']] for r in success),global_designability_of_unscreened_raw_failures='not measured'))
    diversity=[]
    if c.get('assay')=='fragment_repetition_refold':
        from latentfold.fragment_designability import scaffold_rmsd
        with h5py.File(run/'refolded.h5') as refold,h5py.File(c['predictions']) as rawfile:
            for s in c['screens']:
                success=[r for r in records if r['arm']==s['arm'] and r['strict_joint_success'] and positive[r['target_id']]]
                chosen=[dict(name=r['name'],generation_slot=r['generation_slot'],sequence_index=r['successful_refold_indices'][0]) for r in success]
                pairs=[]
                for left,right in itertools.combinations(success,2):
                    x=refold[left['name']+'/'+str(left['successful_refold_indices'][0])][:]
                    y=refold[right['name']+'/'+str(right['successful_refold_indices'][0])][:]
                    keep=np.zeros(len(x),dtype=bool);start=left['motif_start'];keep[start:start+len(rawfile['motifs/'+left['target_id']])]=True
                    pairs.append(dict(left=left['generation_slot'],right=right['generation_slot'],global_tm=usalign_coordinates(c['usalign'],x[:,1],y[:,1]),motif_aligned_scaffold_rmsd=scaffold_rmsd(x,y,keep)))
                diversity.append(dict(arm=s['arm'],successful_backbones=len(success),chosen_first_qualifying_refolds=chosen,pairs=pairs,mean_global_tm=float(np.mean([r['global_tm'] for r in pairs])) if pairs else None,mean_motif_aligned_scaffold_rmsd=float(np.mean([r['motif_aligned_scaffold_rmsd'] for r in pairs])) if pairs else None))
    return dict(status='complete',successful_refold_diversity=diversity,manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),completed_refolds=len(m['records']),native_strict_controls=positive,summaries=summaries,records=records,interpretation='Exploratory raw-screened diagnostic on reused development families; all nonpassing raw samples remain strict failures. This does not replace fixed-panel assays or override failed gates. Overall global designability is not measured, and no development refolds become training labels.',elapsed_seconds=m['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='records'};a.output.with_suffix('.md').write_text('# Refolding every strict raw match\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')


if __name__=='__main__':main()
