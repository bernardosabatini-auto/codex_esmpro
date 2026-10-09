"""A fresh matched same-refold assay after the fixed guidance pilot qualifies."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from context_flow_generation import audit_worker as verify_identity,identity
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from verified_sources import VerifiedSources
from prepare_overfit import sha


def audit_worker(c):
    if c.get('trajectory_guidance_refold') is not True or c['assay']!='fragment_preference_refold':raise ValueError('Wrong guidance assay')
    verify_identity(c)


def entries_and_arrays(gc,fr,gen):
    index=0
    for row in gc['selected']:
        ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center']
        for arm in ('native','baseline','guided'):
            for slot in range(1 if arm=='native' else 4):
                e=make_entry(row,q,slot,index,arm=arm);e.update(repeatability_control=arm=='native');index+=1
                bb=fr['train/'+ident+'/reference_backbone'][:] if arm=='native' else gen[arm+'/'+ident+'/backbone'][slot]
                yield e,bb,q['fragment'][:]


def audit_refold(c):
    audit_worker(c);verifier=VerifiedSources()
    for r in c['sources']:verifier.verify(r)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];d=json.loads(Path(c['generation_report']).read_text());spec=json.loads(Path(c['protocol']).read_text())
    if gm['status']!='complete' or d['status']!='complete' or not d['qualified'] or d['manifest_sha256']!=c['generation_manifest_sha256'] or d['predictions_sha256']!=c['generated_predictions_sha256'] or Path(c['generation_manifest']).parent.name!=spec['generation']:raise ValueError('Unqualified guidance pilot')
    from trajectory_guidance_core import audit
    audit(gc)
    recipe=json.loads(Path(c['teacher_recipe_source']).read_text())['config']
    if any(c[k]!=recipe[k] for k in TEACHER_KEYS) or (c['num_sequences'],c['temperature'],c['mpnn_seed'],c['expected_backbones'],len(c['entries']),c['allocation_minutes'],c['work_cap_seconds'])!=(8,.1,1,36,36,35,2010) or not c['teacher_deterministic_algorithms'] or c['mpnn_mode']!='ca':raise ValueError('Changed matched budget')
    with h5py.File(c['predictions'],locking=False) as inp,h5py.File(gc['fragments'],locking=False) as fr,h5py.File(c['generated_predictions'],locking=False) as gen:
        wanted=[]
        for e,bb,motif in entries_and_arrays(gc,fr,gen):
            wanted.append(e)
            if not np.array_equal(inp[e['dataset']][:],bb[None]) or not np.array_equal(inp['motifs/'+e['target_id']][:],motif):raise ValueError('Changed original motif or candidate')
        if wanted!=c['entries'] or set(inp)!={'motifs',*(e['dataset'] for e in wanted)} or set(inp['motifs'])!={r['id'] for r in gc['selected']}:raise ValueError('Filtered candidate inventory')
    return dict(trajectory_guidance_refold=True),spec


def add_summary(result,spec):
    records=result['records'];summary={}
    for arm in ('native','baseline','guided'):
        rr=[r for r in records if r['arm']==arm]
        summary[arm]=dict(samples=len(rr),raw=sum(r['raw_gate_passed'] for r in rr),strict=sum(r['scaffold_joint_success'] for r in rr),strict_families=len({r['family'] for r in rr if r['scaffold_joint_success']}),designable=sum(r['valid_designable'] for r in rr),global_scaffold=sum(any(x['coarse_valid'] and x['sc_tm']>.5 and x['scaffold_tm']>.5 for x in r['refolds']) for r in rr),connected_strict=sum(r['complete_strict'] for r in rr))
    a,b,n=summary['guided'],summary['baseline'],summary['native'];g=spec['advance']
    gates=dict(strict=a['strict']>=b['strict']+g['minimum_strict_gain'],families=a['strict_families']>=g['minimum_guided_strict_families'],designability=a['designable']>=b['designable']-g['maximum_designability_loss'],native=n['global_scaffold']>=g['minimum_native_global_scaffold'])
    result.update(trajectory_guidance_refold=True,summary=summary,advancement_gates=gates,qualified=all(gates.values()))


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/trajectory_guidance_refold_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['generation'];gm=json.loads((run/'manifest.json').read_text());gc=gm['config']
    recipe=root/'runs/fragment_preference_refold_51491050/manifest.json';rc=json.loads(recipe.read_text())['config'];c={k:rc[k] for k in TEACHER_KEYS}
    c.update(assay='fragment_preference_refold',trajectory_guidance_refold=True,partition=0,expected_backbones=36,entries=[],sources=[],allocation_minutes=35,work_cap_seconds=2010,teacher_deterministic_algorithms=True,mpnn_mode='ca')
    inputs=a.output.with_suffix('.h5').resolve()
    with h5py.File(inputs,'x') as out,h5py.File(gc['fragments'],locking=False) as fr,h5py.File(run/'predictions.h5',locking=False) as gen:
        for e,bb,motif in entries_and_arrays(gc,fr,gen):
            c['entries'].append(e);out[e['dataset']]=bb[None]
            if 'motifs/'+e['target_id'] not in out:out['motifs/'+e['target_id']]=motif
    for key,pth in [('generation_manifest',run/'manifest.json'),('generation_report',root/'reports'/(run.name+'.json')),('generated_predictions',run/'predictions.h5'),('teacher_recipe_source',recipe),('protocol',protocol),('predictions',inputs)]:
        c[key]=str(pth.resolve());c[key+'_sha256']=sha(pth);c['sources'].append(dict(path=c[key],sha256=c[key+'_sha256']))
    c['sources']+=gc['sources']+c['dependencies']+c['teacher_artifacts'];c['file_identity']=[identity(r['path']) for r in c['sources']];c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit_refold(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('36 backbones,288 refolds plus4 repeats,oneRTX35min ceiling')

if __name__=='__main__':main()
