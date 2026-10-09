"""Both entire retrieval arms receive the same original fixed-motif assay."""
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
from context_flow_generation import audit_worker as verify_identity,identity
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from prepare_overfit import sha


def audit_worker(c):
    if not c.get('retrieved_context_refold') or c['assay']!='fragment_preference_refold':
        raise ValueError('Explicit retrieval assay required')
    verify_identity(c)


def audit_refold(c,*,audited_generation=None):
    audit_worker(c)
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed retrieval-refold input')
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];d=json.loads(Path(c['generation_report']).read_text())
    from retrieved_context_profile import audit
    if audited_generation is None:audit(gc)
    bm=json.loads(Path(c['baseline_refold_manifest']).read_text());bc=bm['config'];bd=json.loads(Path(c['baseline_refold_report']).read_text())
    if (gm['status']!='complete' or d['status']!='complete' or not d.get('full_panel') or not d['refold_eligible']
            or not d['qualified'] or d['summary']['retrieved']['raw']<9 or d['summary']['retrieved']['valid']<45
            or d['manifest_sha256']!=sha(c['generation_manifest']) or d['predictions_sha256']!=sha(c['generated_predictions'])
            or c['protocol']!=gc['protocol'] or c['arm'] not in ('retrieved','random')
            or bm['status']!='complete' or bd['status']!='complete' or bd['completed_refolds']!=256
            or bd['manifest_sha256']!=sha(c['baseline_refold_manifest']) or bc['partition']!=c['partition']
            or bc['generation_manifest']!=gc['parent']['baseline_manifest'] or not bm['teacher_deterministic_algorithms']
            or any(c[k]!=bc[k] for k in TEACHER_KEYS) or c['num_sequences']!=8 or c['temperature']!=.1
            or c['expected_backbones']!=32 or len(c['entries'])!=32 or c['partition'] not in range(4)
            or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010
            or c.get('teacher_deterministic_algorithms') is not True or c.get('mpnn_mode')!='ca'):
        raise ValueError('Changed generation, control partition or assay budget')
    rows=[r for r in gc['selected'] if r['partition']==c['partition']];wanted=[]
    with h5py.File(gc['fragments']) as fr,h5py.File(c['predictions']) as inp,h5py.File(c['generated_predictions']) as gen:
        for row in rows:
            ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center']
            if not np.array_equal(inp['motifs/'+ident][:],q['fragment'][:]):raise ValueError('Changed ORIGINAL query motif')
            for slot in range(4):
                entry=make_entry(row,q,slot,len(wanted),arm=c['arm']);wanted.append(entry)
                if not np.array_equal(inp[entry['dataset']][:],gen[c['arm']+'/'+ident+'/backbone'][slot][None]):
                    raise ValueError('Changed candidate or slot')
        if c['entries']!=wanted or set(inp)!={'motifs',*(r['dataset'] for r in wanted)} or set(inp['motifs'])!={r['id'] for r in rows}:
            raise ValueError('Filtered candidate inventory')
    fields=('target_id','family','length','generation_slot','fixed_start','fixed_sequence','repeatability_control')
    if len(bc['entries'])!=32 or any(a[k]!=b[k] for a,b in zip(c['entries'],bc['entries']) for k in fields):
        raise ValueError('Parent/query fixed-motif budgets differ')
    result=dict(arm=c['arm'],retrieved_context_refold=True,selected=gc['selected'],fragments=gc['fragments'],
                native_sources=json.loads(Path(gc['parent']['baseline_manifest']).read_text())['config']['native_sources'],prediction_group=c['arm'])
    if audited_generation is not None and audited_generation!=(result,gc['spec']):raise ValueError('Changed cached source')
    return result,gc['spec']


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--arm',choices=['retrieved','random'],required=True)
    p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    run=a.generation.resolve();gm=json.loads((run/'manifest.json').read_text());gc=gm['config']
    report=root/'reports'/(run.name+'.json');d=json.loads(report.read_text())
    if not d.get('full_panel') or not d.get('refold_eligible'):raise ValueError('Full retrieval generation prerequisite failed')
    from retrieved_context_profile import audit
    audit(gc)
    baseline=json.loads((root/'reports/fragment_preference_comparison_20261003.json').read_text());parents={}
    for source in baseline['sources']:
        rp=Path(source['report'])
        if sha(rp)!=source['report_sha256']:raise ValueError('Changed original parent comparison')
        mp=root/'runs'/rp.stem/'manifest.json';bc=json.loads(mp.read_text())['config'];parents[bc['partition']]=(mp,rp,bc)
    if set(parents)!=set(range(4)):raise ValueError('All four distinct parent partitions required')
    checksum={}
    def checksum_of(path):
        path=str(Path(path).resolve())
        if path not in checksum:checksum[path]=sha(path)
        return checksum[path]
    cached=None
    for partition in range(4):
        mp,rp,bc=parents[partition];path=Path(str(a.output_prefix)+f'_{partition}.json').resolve();inputs=path.with_suffix('.h5')
        c={k:bc[k] for k in TEACHER_KEYS};c.update(retrieved_context_refold=True,assay='fragment_preference_refold',arm=a.arm,
            partition=partition,expected_backbones=32,entries=[],allocation_minutes=35,work_cap_seconds=2010,
            teacher_deterministic_algorithms=True,mpnn_mode='ca',sources=[])
        def bind(key,value):
            value=str(Path(value).resolve());c[key]=value;c[key+'_sha256']=checksum_of(value)
            c['sources'].append(dict(path=value,sha256=c[key+'_sha256']))
        for key,value in [('generation_manifest',run/'manifest.json'),('generation_report',report),('generated_predictions',run/'predictions.h5'),
                          ('protocol',gc['protocol']),('baseline_refold_manifest',mp),('baseline_refold_report',rp)]:bind(key,value)
        with h5py.File(gc['fragments']) as fr,h5py.File(run/'predictions.h5') as gen,h5py.File(inputs,'x') as out:
            for row in (r for r in gc['selected'] if r['partition']==partition):
                q=fr['train/'+row['id']+'/conditions/c20_center'];out.create_dataset('motifs/'+row['id'],data=q['fragment'][:])
                for slot in range(4):
                    entry=make_entry(row,q,slot,len(c['entries']),arm=a.arm);c['entries'].append(entry)
                    out.create_dataset(entry['dataset'],data=gen[a.arm+'/'+row['id']+'/backbone'][slot][None])
        bind('predictions',inputs)
        for r in gc['sources']+c['dependencies']+c['teacher_artifacts']:
            if checksum_of(r['path'])!=r['sha256']:raise ValueError('Changed source or teacher artifact')
            c['sources'].append(r)
        c['file_identity']=[identity(r['path']) for r in c['sources']]
        c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
        cached=audit_refold(c,audited_generation=cached)
        with path.open('x') as f:json.dump(c,f,indent=2)
        print(a.arm,partition,len(c['entries']),flush=True)


if __name__=='__main__':main()
