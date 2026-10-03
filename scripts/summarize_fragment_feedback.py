"""Audit same-refold repaired training targets; never relabel failed retention."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit,same_refold_success,first_repaired_target
from prepare_fragment_feedback import audit_inputs
from fixed_motif_design import verify_fixed_sequences
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),profile_qualified=False,feedback_training_qualified=False)
    c=m['config'];audit_inputs(c);verify_fixed_sequences(m['sequences'],c['entries']);index={(r['name'],r['sequence_index']):r for r in m['records']};wanted={(r['name'],k) for r in c['entries'] for k in range(8)}
    if len(index)!=len(m['records']) or set(index)!=wanted:raise ValueError('Incomplete refold inventory')
    natives={r['name'] for r in c['entries'] if r['mode']=='native'}
    if len(m['controls'])!=len(natives) or {r['name'] for r in m['controls']}!=natives or any(r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Repeatability control failed')
    records=[];targets=[];retest=c.get('feedback_revision')=='weighted6000_scaffold'
    with h5py.File(c['predictions']) as rawfile,h5py.File(run/'refolded.h5') as refold:
        if set(refold)!={r['name'] for r in c['entries']}:raise ValueError('Extra refold group')
        for r in c['entries']:
            name=r['name'];bb=rawfile[r['dataset']][r['slot']];fragment=rawfile['motifs/'+r['target_id']][:];raw=dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**motif_fit(bb,fragment,r['motif_start']));rows=[]
            if set(refold[name])!=set(map(str,range(8))):raise ValueError('Missing designed sequence refold')
            for k in range(8):
                x=refold[name+'/'+str(k)][:]
                if x.shape!=bb.shape or not np.isfinite(x).all():raise ValueError('Invalid saved refold')
                tm=usalign_coordinates(c['usalign'],x[:,1],bb[:,1])
                if abs(tm-index[name,k]['sc_tm'])>1e-7:raise ValueError('Global score mismatch')
                rows.append(dict(sequence_index=k,sc_tm=tm,coarse_valid=bool(backbone_geometry(x[None])['coarse_valid'][0]),**motif_fit(x,fragment,r['motif_start'])))
            if retest:
                keep=np.ones(len(bb),dtype=bool);keep[r['motif_start']:r['motif_start']+len(fragment)]=False
                for k,row in enumerate(rows):row['scaffold_tm']=usalign_coordinates(c['usalign'],refold[name+'/'+str(k)][:][keep,1],bb[keep,1])
            outcome=same_refold_success(raw,rows);record=dict(**r,raw=raw,refolds=rows,**outcome);records.append(record)
            k=first_repaired_target(raw,rows,require_scaffold=retest)
            if retest:
                passing=[i for i in outcome['successful_refold_indices'] if rows[i]['scaffold_tm']>.5]
                record['scaffold_joint_success']=outcome['raw_gate_passed'] and bool(passing)
                record['scaffold_valid_designable']=raw['coarse_valid'] and any(row['coarse_valid'] and row['sc_tm']>.5 and row['scaffold_tm']>.5 for row in rows)
            if r['mode']=='generated' and k is not None:
                targets.append(dict(name=name,target_id=r['target_id'],family=r['family'],generation_slot=r['slot'],sequence_index=k,refold_dataset=name+'/'+str(k),sequence=m['sequences'][name][k],raw_retained=outcome['raw_gate_passed'],**{key:rows[k][key] for key in (('sc_tm','motif_drms','motif_ca_rmsd','scaffold_tm') if retest else ('sc_tm','motif_drms','motif_ca_rmsd'))}))
    native_success=sum(r['valid_designable'] for r in records if r['mode']=='native');families=len({r['family'] for r in targets});peak=max(r['peak_reserved_bytes'] for r in m['records'])/2**30;profile=bool(c['profile_only'] and peak<=75);qualified=bool(not c['profile_only'] and native_success>=6 and len(targets)>=8 and families>=4)
    native_scaffold=sum(r.get('scaffold_valid_designable',False) for r in records if r['mode']=='native')
    if retest:qualified=qualified and native_scaffold>=6 and peak<=75
    return dict(feedback_revision=c.get('feedback_revision'),native_scaffold_valid_global=native_scaffold if retest else None,status='complete',manifest_sha256=sha(path),refolded_sha256=sha(run/'refolded.h5'),generation_manifest_sha256=c['generation_manifest_sha256'],protocol_sha256=c['protocol_sha256'],profile_qualified=profile,feedback_training_qualified=qualified,profile_only=c['profile_only'],backbones=len(records),completed_refolds=len(m['records']),native_valid_global=native_success,native_count=len(natives),generated_strict_retention=sum(r['strict_joint_success'] for r in records if r['mode']=='generated'),qualifying_feedback_backbones=len(targets),qualifying_feedback_families=families,targets_requiring_motif_repair=sum(not r['raw_retained'] for r in targets),targets=targets,records=records,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=peak)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k not in ('records','targets')};a.output.with_suffix('.md').write_text('# Training-only measured designability feedback\n\nEvery candidate and refold retained. Each target comes from one valid refold meeting both motif tolerances and global agreement. Sequence-driven motif repair can produce training labels but does not convert a raw retention failure into a success. This is teacher-consistency supervision on existing training families; no development or locked-test labels.\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n');print(json.dumps(view,indent=2))

if __name__=='__main__':main()
