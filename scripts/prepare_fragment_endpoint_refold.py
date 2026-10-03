"""Bind every paired correction endpoint, without raw-pass filtering."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from fragment_endpoint_core import audit_config
from prepare_overfit import sha

RECIPE=('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')


def audit_inputs(c):
    for key in ('generation_manifest','generation_report','generation_predictions','protocol','fragments','native_predictions','predictions','teacher_recipe_source'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed correction refold input '+key)
    gm=json.loads(Path(c['generation_manifest']).read_text());d=json.loads(Path(c['generation_report']).read_text());gc=gm['config'];spec=audit_config(gc)
    if gm['status']!='complete' or d['status']!='complete' or not d['refold_gate_passed'] or d['manifest_sha256']!=c['generation_manifest_sha256'] or gm['predictions_sha256']!=c['generation_predictions_sha256'] or not spec.get('validity_guarded') or gc['fragments']!=c['fragments'] or gc['protocol']!=c['protocol'] or gc['native_predictions_sha256']!=c['native_predictions_sha256']:raise ValueError('Unqualified or changed correction')
    recipe=json.loads(Path(c['teacher_recipe_source']).read_text())['config']
    if any(c[k]!=recipe[k] for k in RECIPE) or (c['num_sequences'],c['temperature'],c['mpnn_seed'])!=(8,.1,1):raise ValueError('Changed design or teacher recipe')
    wanted={(arm,i,k) for arm in ('initial','guided') for i in gc['target_ids'] for k in range(4)}|{('native',i,0) for i in gc['target_ids']}
    if len(c['entries'])!=36 or c['expected_backbones']!=36 or {(r['arm'],r['target_id'],r['generation_slot']) for r in c['entries']}!=wanted:raise ValueError('Changed full matched inventory')
    with h5py.File(c['predictions']) as out,h5py.File(c['generation_predictions']) as gen,h5py.File(c['fragments']) as fr,h5py.File(c['native_predictions']) as native:
        if set(out)!={'motifs'}|{r['dataset'] for r in c['entries']} or set(out['motifs'])!=set(gc['target_ids']):raise ValueError('Changed stored inventory')
        for r in c['entries']:
            ident=r['target_id'];q=fr['development/'+ident+'/conditions/f30_center'];bb=native['references/'+ident+'/backbone'][:] if r['arm']=='native' else gen[ident+'/'+r['arm']+'_backbone'][r['generation_slot']]
            if not np.array_equal(out[r['dataset']][:],bb[None]) or not np.array_equal(out['motifs/'+ident][:],q['fragment'][:]):raise ValueError('Changed paired backbone or fragment')
            if r['slot']!=0 or r['length']!=len(bb) or r['family']!=str(fr['development/'+ident].attrs['family']) or r['fixed_sequence']!=str(q.attrs['sequence']) or r['fixed_start']!=int(q.attrs['start']) or r['motif_start']!=r['fixed_start'] or r['repeatability_control']!=(r['arm']=='native'):raise ValueError('Changed constraint or control')


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=a.generation.resolve();gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];report=root/'reports'/(run.name+'.json');d=json.loads(report.read_text())
    if d['status']!='complete' or not d['refold_gate_passed']:raise ValueError('Correction gate failed')
    recipe=root/'runs/fragment_validation_refold_50100503/manifest.json';prior=json.loads(recipe.read_text())['config'];c={k:prior[k] for k in RECIPE};c.update(assay='fragment_endpoint_refold',expected_backbones=36,entries=[])
    inputs=a.output.with_suffix('.h5').resolve()
    with h5py.File(gc['fragments']) as fr,h5py.File(run/'predictions.h5') as gen,h5py.File(gc['native_predictions']) as native,h5py.File(inputs,'x') as out:
        for ident in gc['target_ids']:
            q=fr['development/'+ident+'/conditions/f30_center'];out.create_dataset('motifs/'+ident,data=q['fragment'][:])
            for arm in ('native','initial','guided'):
                for k in range(1 if arm=='native' else 4):
                    bb=native['references/'+ident+'/backbone'][:] if arm=='native' else gen[ident+'/'+arm+'_backbone'][k];name=f'endpoint_{len(c["entries"]):03d}';out.create_dataset(name,data=bb[None]);c['entries'].append(dict(name=name,head=arm,arm=arm,target_id=ident,family=str(fr['development/'+ident].attrs['family']),generation_slot=k,slot=0,length=len(bb),dataset=name,motif_start=int(q.attrs['start']),fixed_start=int(q.attrs['start']),fixed_sequence=str(q.attrs['sequence']),repeatability_control=arm=='native'))
    for key,path in [('generation_manifest',run/'manifest.json'),('generation_report',report),('generation_predictions',run/'predictions.h5'),('protocol',Path(gc['protocol'])),('fragments',Path(gc['fragments'])),('native_predictions',Path(gc['native_predictions'])),('predictions',inputs),('teacher_recipe_source',recipe)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    minutes=math.ceil((36*8*6+180)*1.2/60);c.update(allocation_minutes=minutes,work_cap_seconds=60*minutes-90);audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('36backbones,288refolds,allocation minutes',minutes)

if __name__=='__main__':main()
