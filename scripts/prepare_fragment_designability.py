"""Freeze paired fragment-only and full-context backbones without outcome filtering."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from summarize_isolated_motif import analyze


def audit_inputs(c):
 for key in ('generation_manifest','predictions','protocol','source_predictions','reference_predictions'):
  if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
 gm=json.loads(Path(c['generation_manifest']).read_text());ids=gm['config']['control_ids'];wanted={(mode,i,k) for mode in ('full_context','isolated') for i in ids for k in range(2)}|{('real',i,0) for i in ids}
 if len(c['entries'])!=20 or {(r['mode'],r['target_id'],r['slot']) for r in c['entries']}!=wanted:raise ValueError('Incorrect assay coverage')
 with h5py.File(c['predictions']) as inp,h5py.File(c['source_predictions']) as src,h5py.File(c['reference_predictions']) as refs:
  for r in c['entries']:
   i,k,mode=r['target_id'],r['slot'],r['mode'];actual=inp[r['dataset']][:] if mode=='real' else inp[r['dataset']][k];expected=refs[f'references/{i}/backbone'][:] if mode=='real' else (src[i+'/backbone'][k] if mode=='isolated' else refs[f'original50/motif_u3/{i}/backbone'][k])
   if not np.array_equal(actual,expected):raise ValueError('Assay backbone changed')


def main():
 p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];result=analyze(a.generation)
 if result['status']!='complete':raise ValueError('Isolated generation incomplete')
 manifest=a.generation/'manifest.json';gc=json.loads(manifest.read_text())['config'];rows={r['target_id']:r for r in json.loads(Path(gc['selection']).read_text())['rows']};inputs=a.output.with_suffix('.h5');entries=[]
 with h5py.File(inputs,'x') as dest,h5py.File(a.generation/'predictions.h5') as src,h5py.File(gc['parent_predictions']) as refs:
  for ident in gc['control_ids']:
   row=rows[ident]
   for mode in ('real','full_context','isolated'):
    dataset=f'{mode}/{ident}';bb=refs[f'references/{ident}/backbone'][:] if mode=='real' else (src[ident+'/backbone'][:2] if mode=='isolated' else refs[f'original50/motif_u3/{ident}/backbone'][:2]);dest.create_dataset(dataset,data=bb)
    for k in ([0] if mode=='real' else range(2)):
     record=None if mode=='real' else next(r for r in result['records'] if (r['target_id'],r['slot'],r['mode'])==(ident,k,mode));entries.append(dict(name=f'fragment_{len(entries):03d}',head='experimental' if mode=='real' else 'original50',mode=mode,target_id=ident,family=row['family'],slot=k,length=row['length'],dataset=dataset,motif_drms=None if record is None else record['motif_drms']))
 prior=json.loads((root/'runs/designability_49855973/manifest.json').read_text())['config'];c={k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};c.update(assay='isolated_motif',entries=entries,work_cap_seconds=780,decision='All20backbones/all160refolds, no outcome filtering')
 for key,path in [('generation_manifest',manifest),('predictions',inputs),('protocol',root/'configs/fragment_designability_protocol.json'),('source_predictions',a.generation/'predictions.h5'),('reference_predictions',Path(gc['parent_predictions']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
 audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen20backbones,160refolds')
if __name__=='__main__':main()
