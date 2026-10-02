"""Bind a prospective measured-feedback collection to training-only samples."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


KEYS=('generation_manifest','training_report','training_predictions','fragments','predictions','protocol','usalign')


def selected_ids(fragments):
    ordered=sorted(fragments['train'],key=lambda i:(int(fragments['train/'+i].attrs['length']),i))
    if len(ordered)!=32:raise ValueError('Expected original32training proteins')
    return [ordered[k] for k in range(0,32,4)]


def audit_inputs(c):
    for key in KEYS:
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    for r in c['dependencies']+c['teacher_artifacts']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed teacher dependency')
    if Path(c['generation_manifest']).parent.name!='fragment_training_49929751':raise ValueError('Unregistered feedback source')
    m=json.loads(Path(c['generation_manifest']).read_text());d=json.loads(Path(c['training_report']).read_text())
    if m['status']!='complete' or m['updates']!=2000 or m['config']['arm']!='full' or m['config'].get('variant')!='geometry' or m['config'].get('auxiliary_motif') or d['manifest_sha256']!=c['generation_manifest_sha256'] or d['status']!='complete' or c['fragments_sha256']!=m['config']['fragments_sha256']:raise ValueError('Invalid feedback parent')
    with h5py.File(c['fragments']) as fr,h5py.File(c['predictions']) as out,h5py.File(c['training_predictions']) as gen:
        ids=selected_ids(fr)
        if c['selected_training_ids']!=ids or set(ids)&set(fr['development']):raise ValueError('Changed training-only inventory')
        expected={(mode,i,k) for i in ids for mode in ('generated','native') for k in (range(2) if mode=='generated' else [0])}
        if c['profile_only']:expected={('generated',ids[-1],0),('native',ids[-1],0)}
        if len(c['entries'])!=len(expected) or {(r['mode'],r['target_id'],r['slot']) for r in c['entries']}!=expected:raise ValueError('Incorrect feedback inventory')
        for r in c['entries']:
            i,k=r['target_id'],r['slot'];g=fr['train/'+i];q=g['conditions/f30_center'];expectedbb=g['reference_backbone'][:] if r['mode']=='native' else gen['train/conditioned/'+i+'/backbone'][k]
            if r['family']!=g.attrs['family'] or r['length']!=int(g.attrs['length']) or r['fixed_sequence']!=q.attrs['sequence'] or r['fixed_start']!=int(q.attrs['start']) or r['motif_start']!=r['fixed_start']:raise ValueError('Training condition changed')
            if not np.array_equal(out[r['dataset']][k],expectedbb) or not np.array_equal(out['motifs/'+i][:],q['fragment'][:]):raise ValueError('Feedback source arrays changed')
            if r.get('repeatability_control',False)!=(r['mode']=='native'):raise ValueError('Missing native repeat')


def main():
    p=argparse.ArgumentParser();p.add_argument('--training',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--profile',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=a.training/'manifest.json';m=json.loads(manifest.read_text());d=json.loads(a.report.read_text())
    if m['status']!='complete' or m['updates']!=2000 or d['status']!='complete' or d['manifest_sha256']!=sha(manifest):raise ValueError('Audited completed parent required')
    prior=json.loads((root/'runs/trained_fragment_designability_49919660/manifest.json').read_text())['config'];c={k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};inputs=a.output.with_suffix('.h5');entries=[];profile=a.profile is None
    with h5py.File(m['config']['fragments']) as fr,h5py.File(a.training/'evaluation_2000.h5') as gen,h5py.File(inputs,'x') as out:
        ids=selected_ids(fr)
        for i in (ids[-1:] if profile else ids):
            g=fr['train/'+i];q=g['conditions/f30_center'];out.create_dataset('motifs/'+i,data=q['fragment'][:])
            for mode in ('native','generated'):
                bb=g['reference_backbone'][:][None] if mode=='native' else gen['train/conditioned/'+i+'/backbone'][:1 if profile else 2];dataset=mode+'/'+i;out.create_dataset(dataset,data=bb)
                for k in range(len(bb)):entries.append(dict(name=f'feedback_{len(entries):03d}',head='training_native' if mode=='native' else 'geometry_full',mode=mode,target_id=i,family=str(g.attrs['family']),slot=k,length=int(g.attrs['length']),dataset=dataset,motif_start=int(q.attrs['start']),fixed_start=int(q.attrs['start']),fixed_sequence=str(q.attrs['sequence']),repeatability_control=mode=='native'))
    c.update(assay='fragment_feedback_profile' if profile else 'fragment_feedback',profile_only=profile,selected_training_ids=ids,entries=entries,work_cap_seconds=480)
    for key,path in [('generation_manifest',manifest),('training_report',a.report),('training_predictions',a.training/'evaluation_2000.h5'),('fragments',Path(m['config']['fragments'])),('predictions',inputs),('protocol',root/'configs/fragment_feedback_protocol.json')]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if a.profile:
        pd=json.loads(a.profile.read_text())
        if not pd['profile_qualified'] or pd['generation_manifest_sha256']!=c['generation_manifest_sha256'] or pd['protocol_sha256']!=c['protocol_sha256']:raise ValueError('Profile lineage failed')
        minutes=max(15,math.ceil((pd['elapsed_seconds']*12*1.2+180)/60));c.update(profile_report=str(a.profile.resolve()),profile_report_sha256=sha(a.profile),allocation_minutes=minutes,work_cap_seconds=minutes*60-90);print('Feedback allocation minutes',minutes)
    audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
