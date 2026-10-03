"""Freeze unfiltered trained, clamp and null samples under one design budget."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from latentfold.fragment_designability import motif_error


SOURCE_KEYS=('generation_manifest','training_report','training_predictions','fragments','isolated_predictions','reference_predictions','predictions','protocol','selection','usalign')


def audit_inputs(c,check_teacher=True):
    for key in SOURCE_KEYS:
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if check_teacher:
        for dependency in c['dependencies']+c['teacher_artifacts']:
            if sha(dependency['path'])!=dependency['sha256']:raise ValueError('Changed dependency '+dependency['path'])
    m=json.loads(Path(c['generation_manifest']).read_text());report=json.loads(Path(c['training_report']).read_text());ids=m['config']['control_ids'];rows={r['target_id']:r for r in json.loads(Path(c['selection']).read_text())['rows']}
    if m['status']!='complete' or m['updates']!=m['config']['updates'] or m['config']['profile_only'] or report['status']!='complete' or report['manifest_sha256']!=c['generation_manifest_sha256'] or report['config']!=m['config']:raise ValueError('Unqualified training provenance')
    if c.get('training_step',2000) not in m['config']['evaluation_steps'] or Path(c['training_predictions']).name!=f"evaluation_{c.get('training_step',2000)}.h5":raise ValueError('Changed evaluation checkpoint')
    if c['fragments_sha256']!=m['config']['fragments_sha256'] or c['reference_predictions_sha256']!=m['config']['initial_predictions_sha256']:raise ValueError('Changed training inputs')
    wanted={(mode,i,k) for mode in ('conditioned','trained_null','isolated_clamp','original_null') for i in ids for k in range(2)}|{('real',i,0) for i in ids}
    if len(c['entries'])!=36 or {(r['mode'],r['target_id'],r['slot']) for r in c['entries']}!=wanted or len({r['name'] for r in c['entries']})!=36:raise ValueError('Incorrect assay coverage')
    with h5py.File(c['predictions']) as inp,h5py.File(c['training_predictions']) as trained,h5py.File(c['isolated_predictions']) as isolated,h5py.File(c['reference_predictions']) as refs,h5py.File(c['fragments']) as fragments:
        for r in c['entries']:
            i,k,mode=r['target_id'],r['slot'],r['mode'];q=fragments['development/'+i+'/conditions/f30_center'];st=int(q.attrs['start']);fragment=q['fragment'][:];n=rows[i]['length'];seq=str(q.attrs['sequence'])
            actual=inp[r['dataset']][:] if mode=='real' else inp[r['dataset']][k]
            if mode=='real':expected=refs[f'references/{i}/backbone'][:]
            elif mode=='isolated_clamp':expected=isolated[i+'/backbone'][k]
            elif mode=='original_null':expected=refs[f'original50/unconditional/{i}/backbone'][k]
            else:expected=trained[f"development/{'null' if mode=='trained_null' else 'conditioned'}/{i}/backbone"][k]
            if not np.array_equal(actual,expected) or not np.array_equal(inp['motifs/'+i][:],fragment):raise ValueError('Changed source backbone/motif')
            if r['length']!=n or r['family']!=rows[i]['family'] or r['fixed_sequence']!=('' if mode=='real' else seq) or r['fixed_start']!=(0 if mode=='real' else st) or r['motif_start']!=st:raise ValueError('Invalid supplied motif sequence/placement')
            error=float(motif_error(actual[None,st:st+len(fragment)],fragment,np.ones(len(fragment),bool))[0])
            if abs(error-r['motif_drms'])>1e-6:raise ValueError('Raw motif score changed')


def main():
    p=argparse.ArgumentParser();p.add_argument('--training',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--step',type=int,choices=[500,2000]);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=a.training/'manifest.json';m=json.loads(manifest.read_text());report=json.loads(a.report.read_text())
    if m['status']!='complete' or m['updates']!=m['config']['updates'] or m['config']['profile_only'] or report['status']!='complete' or report['manifest_sha256']!=sha(manifest):raise ValueError('Incomplete or unaudited training')
    step=a.step or m['updates']
    if step not in m['config']['evaluation_steps']:raise ValueError('Unavailable endpoint')
    initial=Path(m['config']['initial_predictions']);isolated=root/'runs/isolated_motif_49864561/predictions.h5';fragments=Path(m['config']['fragments']);data=json.loads(Path(m['config']['data_manifest']).read_text());selection=Path(data['config']['selection']);rows={r['target_id']:r for r in json.loads(selection.read_text())['rows']};inputs=a.output.with_suffix('.h5');entries=[];head_name='geometry_teacher_augmented' if m['config'].get('augmentation_protocol') else 'geometry_time_shift' if m['config'].get('time_protocol') else 'geometry_latent_weight3' if m['config'].get('latent_motif_weight') else 'geometry_backbone_tokens' if m['config'].get('backbone_tokens') else 'geometry_sequence_only' if m['config'].get('fragment_representation')=='geometry_sequence' else 'geometry_full_target_frame' if m['config'].get('target_frame_training') else 'geometry_full_rollout_expanded' if m['config'].get('rollout_motif') and m['config'].get('expanded_fragment_data') else 'geometry_full_rollout' if m['config'].get('rollout_motif') else 'geometry_full_expanded512' if m['config'].get('training_protein_count')==512 else 'geometry_full_expanded' if m['config'].get('expanded_fragment_data') else 'geometry_full_continued' if m['config'].get('warm_start') else 'geometry_motif_objective' if m['config'].get('auxiliary_motif') else 'geometry_full' if m['config'].get('variant')=='geometry' and m['config']['arm']=='full' else m['config'].get('variant',m['config']['arm'])
    if step!=2000:head_name+=f'_step{step}'
    with h5py.File(inputs,'x') as out,h5py.File(a.training/f'evaluation_{step}.h5') as trained,h5py.File(initial) as refs,h5py.File(isolated) as iso,h5py.File(fragments) as fr:
        for ident in m['config']['control_ids']:
            row=rows[ident];q=fr['development/'+ident+'/conditions/f30_center'];fragment=q['fragment'][:];st=int(q.attrs['start']);out.create_dataset('motifs/'+ident,data=fragment)
            for mode in ('real','conditioned','trained_null','isolated_clamp','original_null'):
                if mode=='real':bb=refs['references/'+ident+'/backbone'][:]
                elif mode=='isolated_clamp':bb=iso[ident+'/backbone'][:2]
                elif mode=='original_null':bb=refs['original50/unconditional/'+ident+'/backbone'][:2]
                else:bb=trained[f"development/{'null' if mode=='trained_null' else 'conditioned'}/{ident}/backbone"][:2]
                dataset=mode+'/'+ident;out.create_dataset(dataset,data=bb)
                for slot in ([0] if mode=='real' else range(2)):
                    one=bb if mode=='real' else bb[slot];error=float(motif_error(one[None,st:st+len(fragment)],fragment,np.ones(len(fragment),bool))[0]);entries.append(dict(name=f'trained_fragment_{len(entries):03d}',head='experimental' if mode=='real' else head_name if mode in ('conditioned','trained_null') else 'original50',mode=mode,target_id=ident,family=row['family'],slot=slot,length=row['length'],dataset=dataset,motif_drms=error,motif_start=st,fixed_start=0 if mode=='real' else st,fixed_sequence='' if mode=='real' else str(q.attrs['sequence'])))
    prior=json.loads((root/'runs/designability_49855973/manifest.json').read_text())['config'];c={k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};c.update(assay='trained_fragment',entries=entries,work_cap_seconds=1080,arm=head_name,training_step=step,decision='All36backbones,288refolds, fixed motif residues and same-refold joint criterion; no outcome filtering')
    for key,path in [('generation_manifest',manifest),('training_report',a.report),('training_predictions',a.training/f'evaluation_{step}.h5'),('fragments',fragments),('isolated_predictions',isolated),('reference_predictions',initial),('predictions',inputs),('protocol',root/'configs/trained_fragment_designability_protocol.json'),('selection',selection)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    # The GPU consumer verifies every teacher artifact before creating its manifest.
    audit_inputs(c,check_teacher=False);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Prepared36backbones,288refolds')

if __name__=='__main__':main()
