"""Repeat the fixed training-only feedback panel using the improved parent."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha

KEYS=('original_manifest','original_report','original_fragments')
TEACHER_KEYS=('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')


def audit_retest(c):
    for key in KEYS:
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed retest source '+key)
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['generation_manifest']).read_text());d=json.loads(Path(c['training_report']).read_text());old=json.loads(Path(c['original_manifest']).read_text());od=json.loads(Path(c['original_report']).read_text())
    if Path(c['generation_manifest']).parent.name!=spec['parent'] or Path(c['original_manifest']).parent.name!=spec['original_collection'] or c['profile_only'] or c['assay']!='fragment_feedback':raise ValueError('Wrong feedback contrast')
    if m['status']!='complete' or d['status']!='complete' or d['total_training_updates']!=6000 or d['manifest_sha256']!=c['generation_manifest_sha256'] or c['fragments_sha256']!=m['config']['fragments_sha256']:raise ValueError('Unaudited parent')
    if old['status']!='complete' or od['status']!='complete' or od['manifest_sha256']!=c['original_manifest_sha256'] or od['completed_refolds']!=192 or od['peak_reserved_GiB']>75 or old['config']['fragments_sha256']!=c['original_fragments_sha256']:raise ValueError('Wrong original resource profile')
    if any(c[k]!=old['config'][k] for k in TEACHER_KEYS) or c['selected_training_ids']!=old['config']['selected_training_ids'] or c['entries']!=old['config']['entries']:raise ValueError('Changed fixed panel or teacher')
    with h5py.File(c['fragments']) as fr,h5py.File(c['original_fragments']) as original,h5py.File(c['training_predictions']) as gen,h5py.File(c['predictions']) as out:
        ids=c['selected_training_ids']
        if len(ids)!=8 or len(c['entries'])!=24 or set(ids)&set(fr['development']):raise ValueError('Not the training-only panel')
        for r in c['entries']:
            i,k=r['target_id'],r['slot'];g=fr['train/'+i];q=g['conditions/f30_center'];oq=original['train/'+i+'/conditions/f30_center']
            expected=g['reference_backbone'][:] if r['mode']=='native' else gen['train/conditioned/'+i+'/backbone'][k]
            if r['family']!=g.attrs['family'] or r['length']!=g.attrs['length'] or r['fixed_sequence']!=q.attrs['sequence'] or r['motif_start']!=int(q.attrs['start']) or r['fixed_start']!=r['motif_start'] or r['repeatability_control']!=(r['mode']=='native'):raise ValueError('Changed condition metadata')
            if not np.array_equal(q['fragment'][:],oq['fragment'][:]) or q.attrs['sequence']!=oq.attrs['sequence'] or q.attrs['start']!=oq.attrs['start'] or not np.array_equal(g['reference_backbone'][:],original['train/'+i+'/reference_backbone'][:]):raise ValueError('Changed original training task')
            if not np.array_equal(out[r['dataset']][k],expected) or not np.array_equal(out['motifs/'+i][:],q['fragment'][:]):raise ValueError('Changed feedback arrays')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_feedback_retest_protocol.json';spec=json.loads(protocol.read_text());parent=root/'runs'/spec['parent'];oldrun=root/'runs'/spec['original_collection'];old=json.loads((oldrun/'manifest.json').read_text());od=json.loads((root/'reports'/(oldrun.name+'.json')).read_text());m=json.loads((parent/'manifest.json').read_text());c={k:old['config'][k] for k in TEACHER_KEYS};minutes=max(10,math.ceil((od['elapsed_seconds']*1.5+180)/60));c.update(assay='fragment_feedback',feedback_revision='weighted6000_scaffold',profile_only=False,selected_training_ids=old['config']['selected_training_ids'],entries=old['config']['entries'],allocation_minutes=minutes,work_cap_seconds=minutes*60-90)
    inputs=a.output.with_suffix('.h5').resolve()
    with h5py.File(m['config']['fragments']) as fr,h5py.File(parent/'evaluation_2000.h5') as gen,h5py.File(inputs,'x') as out:
        for i in c['selected_training_ids']:
            out.create_dataset('motifs/'+i,data=fr['train/'+i+'/conditions/f30_center/fragment'][:]);out.create_dataset('native/'+i,data=fr['train/'+i+'/reference_backbone'][:][None]);out.create_dataset('generated/'+i,data=gen['train/conditioned/'+i+'/backbone'][:2])
    for key,path in [('generation_manifest',parent/'manifest.json'),('training_report',root/'reports'/(parent.name+'.json')),('training_predictions',parent/'evaluation_2000.h5'),('fragments',Path(m['config']['fragments'])),('predictions',inputs),('protocol',protocol),('original_manifest',oldrun/'manifest.json'),('original_report',root/'reports'/(oldrun.name+'.json')),('original_fragments',Path(old['config']['fragments']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    from prepare_fragment_feedback import audit_inputs
    audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('192refolds; allocation minutes',minutes)


if __name__=='__main__':main()
