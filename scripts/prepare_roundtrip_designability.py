"""Bind a reconstruction diagnostic to existing audited refold labels."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def audit_sources(c):
    for key in ('protocol','inputs','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    for source in c['sources']:
        for key in ('manifest','report','predictions'):
            if sha(source[key])!=source[key+'_sha256']:raise ValueError('Changed diagnostic source')
        m=json.loads(Path(source['manifest']).read_text());r=json.loads(Path(source['report']).read_text())
        if m['status']!='complete' or r['status']!='complete' or r['manifest_sha256']!=source['manifest_sha256'] or m['config']['predictions_sha256']!=source['predictions_sha256']:raise ValueError('Unqualified refold label source')
    wanted=set()
    for i,source in enumerate(c['sources']):
        r=json.loads(Path(source['report']).read_text());records=r['records'] if i==0 else r['backbones'];wanted.update((i,x['name']) for x in records if i==0 or x['mode']=='conditioned' or i==1 and x['mode']=='real')
    if {(r['source_index'],r['source_name']) for r in c['entries']}!=wanted:raise ValueError('Changed source coverage')
    if len(c['entries'])!=76 or len({r['name'] for r in c['entries']})!=76:raise ValueError('Wrong diagnostic coverage')
    with h5py.File(c['inputs']) as f:
        if set(f)!={r['name'] for r in c['entries']}:raise ValueError('Changed input inventory')
        for r in c['entries']:
            source=c['sources'][r['source_index']];report=json.loads(Path(source['report']).read_text());records=report['records'] if r['source_index']==0 else report['backbones'];entry=next(x for x in records if x['name']==r['source_name'])
            if bool(entry['valid_designable'])!=r['designable'] or bool(entry['strict_joint_success'])!=r['strict'] or entry['family']!=r['family'] or bool(entry['raw']['coarse_valid'])!=r['raw_valid'] or entry['target_id']!=r['target_id'] or entry['slot']!=r['slot']:raise ValueError('Changed label')
            with h5py.File(source['predictions']) as original:
                expected=original[entry['dataset']][:] if entry['mode']=='real' else original[entry['dataset']][entry['slot']]
            if not np.array_equal(f[r['name']][:],expected):raise ValueError('Changed raw backbone')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];sources=[];entries=[];inputs=a.output.with_suffix('.h5')
    ids=['fragment_feedback_49941786']+['trained_fragment_designability_'+j for j in ['49900262','49903663','49919660','49933169','49938555','49949949']]
    with h5py.File(inputs,'x') as out:
        for index,ident in enumerate(ids):
            mp=root/'runs'/ident/'manifest.json';rp=root/'reports'/f'{ident}.json';m=json.loads(mp.read_text());report=json.loads(rp.read_text());source={}
            for key,path in [('manifest',mp),('report',rp),('predictions',Path(m['config']['predictions']))]:source[key]=str(path.resolve());source[key+'_sha256']=sha(path)
            sources.append(source)
            records=report['records'] if index==0 else report['backbones']
            with h5py.File(source['predictions']) as f:
                for r in records:
                    if index and r['mode']!='conditioned' and not(index==1 and r['mode']=='real'):continue
                    cohort=('training' if r['mode']=='generated' else 'training_native') if index==0 else ('development' if r['mode']=='conditioned' else 'development_native');bb=f[r['dataset']][:] if r['mode']=='real' else f[r['dataset']][r['slot']];name=f'cycle_{len(entries):03d}';out.create_dataset(name,data=bb)
                    entries.append(dict(name=name,cohort=cohort,family=r['family'],target_id=r['target_id'],slot=r['slot'],length=len(bb),designable=bool(r['valid_designable']),strict=bool(r['strict_joint_success']),raw_valid=bool(r['raw']['coarse_valid']),source_index=index,source_name=r['name']))
    parent=json.loads((root/'runs/fragment_training_49929751/manifest.json').read_text())['config'];c=dict(seed=2026100244,sources=sources,entries=entries,work_cap_seconds=480)
    for key,path in [('inputs',inputs),('protocol',root/'configs/roundtrip_designability_protocol.json'),('decoder_checkpoint',Path(parent['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    c['control_names']=[max((r for r in entries if r['cohort']==cohort),key=lambda r:(r['length'],r['name']))['name'] for cohort in ['training','training_native','development','development_native']];audit_sources(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Prepared76backbones,152reconstructions')

if __name__=='__main__':main()
