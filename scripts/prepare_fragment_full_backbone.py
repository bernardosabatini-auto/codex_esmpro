"""Freeze an identical-backbone sequence-design comparison, reusing CA-only assays."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def audit_inputs(c,check_teacher=False):
    for r in c['input_sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed full-backbone design source')
    spec=json.loads(Path(c['protocol']).read_text());baseline=json.loads(Path(c['baseline_report']).read_text())
    if c['mpnn_mode']!='backbone' or c['num_sequences']!=8 or c['temperature']!=.1 or c['mpnn_seed']!=1 or baseline['status']!='complete' or c['baseline_records']!=baseline['records']:raise ValueError('Changed design contrast')
    if set(spec['cases'])!={r['target_id'] for r in c['entries']} or len(c['entries'])!=4:raise ValueError('Changed selected cases')
    if check_teacher:
        for r in c['dependencies']+c['teacher_artifacts']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed teacher/design dependency')
    with h5py.File(c['predictions']) as out:
        for r in c['entries']:
            source=r['source'];m=json.loads(Path(source['manifest']).read_text());e=next(x for x in m['config']['entries'] if x['name']==source['name'])
            with h5py.File(m['config']['predictions']) as raw:
                if not np.array_equal(out[r['dataset']][0],raw[e['dataset']][e['slot']]) or not np.array_equal(out['motifs/'+r['target_id']][:],raw['motifs/'+r['target_id']][:]):raise ValueError('Changed raw/native backbone or motif')
            if r['name']!=e['name'] or r['fixed_sequence']!=e['fixed_sequence'] or r['fixed_start']!=e['fixed_start'] or r['motif_start']!=e['motif_start'] or r['length']!=e['length'] or r['repeatability_control']!=(r['arm']=='native'):raise ValueError('Changed design inputs or seeds')
            for k in ('seed','precision','num_sequences','temperature','mpnn_seed','teacher_artifacts'):
                if c[k]!=m['config'][k]:raise ValueError('Changed refolding recipe')
    weight=str(Path(c['mpnn'])/'vanilla_model_weights/v_48_020.pt')
    if weight not in {r['path'] for r in c['dependencies']}:raise ValueError('Unbound full-backbone model')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_full_backbone_protocol.json';spec=json.loads(protocol.read_text());bp=root/'reports'/(spec['baseline_report']+'.json');b=json.loads(bp.read_text());inputs=a.output.with_suffix('.h5')
    prior=json.loads((root/'runs/fragment_strict_followup_50030977/manifest.json').read_text())['config'];c={k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')}
    c.update(assay='fragment_full_backbone',mpnn_mode='backbone',expected_backbones=4,entries=[],input_sources=[],baseline_report=str(bp),baseline_records=b['records'],work_cap_seconds=600)
    def bind(path):
        path=Path(path).resolve();r=dict(path=str(path),sha256=sha(path))
        if r not in c['input_sources']:c['input_sources'].append(r)
        return str(path)
    bind(bp)
    with h5py.File(inputs,'x') as out:
        for r in b['records']:
            src=Path(r.get('reused_from',root/'runs'/spec['baseline_report']));mp=src/'manifest.json';m=json.loads(mp.read_text());name=r.get('source_name',r['name']);e=next(x for x in m['config']['entries'] if x['name']==name)
            if m['status']!='complete' or sha(mp)!=r.get('source_manifest_sha256',b['manifest_sha256']):raise ValueError('Changed audited baseline')
            bind(mp);bind(m['config']['predictions']);bind(src/'refolded.h5')
            with h5py.File(m['config']['predictions']) as f:
                bb=f[e['dataset']][e['slot']];fragment=f['motifs/'+r['target_id']][:]
            out.create_dataset(name,data=bb[None])
            if 'motifs/'+r['target_id'] not in out:out.create_dataset('motifs/'+r['target_id'],data=fragment)
            c['entries'].append(dict(name=name,head=r['arm'],arm=r['arm'],target_id=r['target_id'],family=r['family'],dataset=name,slot=0,length=len(bb),motif_start=e['motif_start'],fixed_start=e['fixed_start'],fixed_sequence=e['fixed_sequence'],repeatability_control=r['arm']=='native',source=dict(manifest=str(mp),name=name)))
    weights=Path(c['mpnn'])/'vanilla_model_weights/v_48_020.pt'
    c['dependencies']=[r for r in c['dependencies'] if '/ca_model_weights/' not in r['path']]+[dict(path=str(weights),sha256=sha(weights))]
    for k,path in [('generation_manifest',root/'runs/fragment_training_50019364/manifest.json'),('predictions',inputs),('protocol',protocol)]:c[k]=bind(path);c[k+'_sha256']=sha(path)
    audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
