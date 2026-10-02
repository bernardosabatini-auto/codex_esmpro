"""Freeze the declared4-family design/refold profile from audited generation."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_generative_pilot import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    result=analyze(a.generation)
    if result['status']!='complete':raise ValueError('Generation incomplete')
    manifest=a.generation/'manifest.json';m=json.loads(manifest.read_text());gc=m['config'];rows=json.loads(Path(gc['selection']).read_text())['rows'];selected=[r for r in rows if r['target_id'] in gc['control_ids']]
    if len(selected)!=4:raise ValueError('Missing fixed pilot families')
    entries=[]
    for row in selected:entries.append(dict(name=f'real_{len(entries):03d}',head='experimental',mode='real',target_id=row['target_id'],family=row['family'],slot=0,length=row['length'],dataset='references/'+row['target_id']+'/backbone',motif_drms=None))
    for h in gc['heads']:
        for mode in gc['modes']:
            for row in selected:
                for k in (0,1):
                    record=next(r for r in m['records'] if (r['head'],r['mode'],r['target_id'],r['slot'])==(h['name'],mode,row['target_id'],k));entries.append(dict(name=f'generated_{len(entries):03d}',head=h['name'],mode=mode,target_id=row['target_id'],family=row['family'],slot=k,length=row['length'],dataset=h['name']+'/'+mode+'/'+row['target_id']+'/backbone',motif_drms=record['motif_drms']))
    source=Path('/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae');mpnn=source/'tools/ProteinMPNN';deps=[mpnn/'protein_mpnn_run.py',mpnn/'protein_mpnn_utils.py',mpnn/'helper_scripts/parse_multiple_chains.py',mpnn/'ca_model_weights/v_48_020.pt']
    c=dict(entries=entries,num_sequences=8,temperature=.1,mpnn_seed=1,seed=2026100212,mpnn=str(mpnn),dependencies=[dict(path=str(x),sha256=sha(x)) for x in deps],work_cap_seconds=2280,precision='fp32',decision='Profile only:4families/2seeds. Require all416refolds and repeatability controls; experimental positive-control failure stops interpretation. Expansion depends on complete assay and measured deadline fit, not favorable candidate geometry.')
    for key,path in [('generation_manifest',manifest),('predictions',a.generation/'predictions.h5'),('protocol',Path(gc['protocol'])),('usalign',root/'runs/tools/USalign/USalign')]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    c['teacher_artifacts']=[dict(path=str(x),sha256=sha(x)) for x in sorted((source/'data/esmfold2_fast').glob('*')) if x.suffix in ('.safetensors','.json')]
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen',len(entries),'backbones',len(entries)*8,'refolds')

if __name__=='__main__':main()
