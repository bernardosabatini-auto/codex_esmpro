"""Export all strict teacher completions with identical isolated student inputs."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from compare_fragment_repaint_teacher import teacher_gate
from compare_native_anchor_models import verify_outcome
from teacher_coordinates_profile_core import sha


def prepare(root, output):
    protocol = root/'configs/repaint_student_pilot_protocol.json'
    spec = json.loads(protocol.read_text())
    comparison = root/spec['qualification']; report = json.loads(comparison.read_text())
    total = next(r for r in report['summary'] if r['arm']=='oracle_repaint' and r['bucket'] is None)
    if report['status']!='complete' or report.get('oracle_teacher') is not True or not teacher_gate(total):
        raise ValueError('Teacher did not qualify for an isolated-input pilot')
    sources = {}
    def bind(path):
        path = Path(path).resolve(); sources[str(path)] = sha(path); return str(path)
    bind(protocol); bind(comparison)
    rows = []; generation = None
    for source in report['source_reports']:
        path = Path(source['path'])
        if sha(path)!=source['sha256']: raise ValueError('Changed comparison source')
        d = json.loads(path.read_text())
        if not any(r['arm']=='oracle_repaint' for r in d['records']): continue
        bind(path); run=root/'runs'/path.stem; mp=run/'manifest.json'; m=json.loads(mp.read_text())
        if (m['status']!='complete' or d['status']!='complete' or d['completed_refolds']!=256
                or sha(mp)!=d['manifest_sha256'] or sha(run/'refolded.h5')!=d['refolded_sha256']):
            raise ValueError('Changed teacher refolding provenance')
        bind(mp); bind(run/'refolded.h5'); c=m['config']
        for key in ('generation_manifest','generation_report','generated_predictions'):
            if sha(c[key])!=c[key+'_sha256']: raise ValueError('Changed teacher generation')
            bind(c[key])
        gm=json.loads(Path(c['generation_manifest']).read_text())
        if generation is not None and generation!=gm: raise ValueError('Mixed teacher generations')
        generation=gm
        for r in d['records']:
            verify_outcome(r)
            if r['arm']!='oracle_repaint': raise ValueError('Mixed teacher partition')
            rows.append(r)
    if len(rows)!=128 or len({(r['target_id'],r['generation_slot']) for r in rows})!=128:
        raise ValueError('Incomplete teacher population')
    positive=sorted((r for r in rows if r['scaffold_joint_success']),key=lambda r:(r['target_id'],r['generation_slot']))
    if len(positive)!=13 or len({r['family'] for r in positive})!=9:
        raise ValueError('Prospective 13-slot/9-family inventory changed')
    gc=generation['config']; fragments=bind(gc['fragments'])
    predictions=Path(c['generated_predictions']); parent=root/'runs'/spec['parent']
    parent_manifest=bind(parent/'manifest.json'); checkpoint=bind(parent/spec['checkpoint'])
    decoder_checkpoint=bind(gc['decoder_checkpoint'])
    # Teacher endpoints are targets. Conditioning comes exclusively from the
    # original isolated-fragment corpus and is identical in both training arms.
    output.mkdir(parents=True,exist_ok=False); exported=[]
    with h5py.File(fragments) as fr,h5py.File(predictions) as gen,h5py.File(output/'labels.h5','x') as out:
        for index,r in enumerate(positive):
            ident=r['target_id'];slot=r['generation_slot'];native=fr['train/'+ident]
            q=native['conditions/'+spec['condition']];g=out.create_group(f'label_{index:02d}')
            teacher=gen['new/'+ident+'/latent'][slot];reference=native['reference_z'][:]
            if teacher.shape!=reference.shape or teacher.shape!=(r['length'],8) or not np.isfinite(teacher).all():
                raise ValueError('Invalid generated latent endpoint')
            if str(q.attrs['sequence'])!=r['fixed_sequence'] or int(q.attrs['start'])!=r['fixed_start']:
                raise ValueError('Changed isolated constraint')
            g['repaint_positive']=teacher;g['native_matched']=reference
            g['fragment_latent']=q['latent'][:];g['fragment']=q['fragment'][:]
            g.attrs.update(target_id=ident,sequence=str(q.attrs['sequence']),start=int(q.attrs['start']),length=r['length'])
            exported.append(dict(label_id=g.name[1:],target_id=ident,family=r['family'],bucket=r['bucket'],length=r['length'],generation_slot=slot,
                                 strict_refold_indices=r['scaffold_successful_refold_indices']))
    # Retain every attempt for each positive, not only its successful refold.
    d=dict(status='complete',spec=spec,rows=exported,qualification_records=positive,
           labels=str((output/'labels.h5').resolve()),labels_sha256=sha(output/'labels.h5'),
           parent_manifest=parent_manifest,checkpoint=checkpoint,decoder_checkpoint=decoder_checkpoint,fragments=fragments,
           sources=[dict(path=k,sha256=v) for k,v in sorted(sources.items())],
           scope='Thirteen selected teacher completions in nine training families; isolated conditioning only. Labels are not evidence of student improvement.')
    (output/'manifest.json').write_text(json.dumps(d,indent=2)+'\n')
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=prepare(Path(__file__).resolve().parents[1],a.output.resolve())
    print(json.dumps(dict(status=d['status'],labels=len(d['rows']),families=len({r['family'] for r in d['rows']}))))


if __name__=='__main__':main()
