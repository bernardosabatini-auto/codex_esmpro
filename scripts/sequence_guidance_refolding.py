"""Same-budget evaluation of the qualified joint sequence/geometry objective."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from context_flow_generation import audit_worker as verify_identity,identity
from verified_sources import VerifiedSources
from prepare_overfit import sha
from trajectory_guidance_refolding import add_summary as paired_summary


def audit_worker(c):
    if c.get('sequence_guidance_refold') is not True or c['assay']!='fragment_preference_refold':raise ValueError('Wrong joint guidance assay')
    verify_identity(c)


def validate_pairing(entries,baseline):
    left={(r['target_id'],r['generation_slot']):r for r in entries};right={(r['target_id'],r['generation_slot']):r for r in baseline}
    if len(left)!=len(entries) or len(right)!=len(baseline) or set(left)!=set(right):raise ValueError('Unpaired/duplicate fixed-budget cases')
    for key,a in left.items():
        if any(a[k]!=right[key][k] for k in ('family','length','fixed_start','motif_start','fixed_sequence')):raise ValueError('Changed original constraint in baseline comparison')


def audit_refold(c):
    audit_worker(c);verifier=VerifiedSources()
    for r in c['sources']:verifier.verify(r)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];d=json.loads(Path(c['generation_report']).read_text());spec=json.loads(Path(c['protocol']).read_text());bm=json.loads(Path(c['baseline_refold_manifest']).read_text());bd=json.loads(Path(c['baseline_refold_report']).read_text());bc=bm['config']
    if gm['status']!='complete' or d['status']!='complete' or not d['qualified'] or not d.get('joint_sequence_guidance') or d['manifest_sha256']!=c['generation_manifest_sha256'] or d['predictions_sha256']!=c['generated_predictions_sha256'] or Path(c['generation_manifest']).parent.name!=spec['generation']:raise ValueError('Unqualified new objective')
    if bm['status']!='complete' or bd['status']!='complete' or bd['manifest_sha256']!=c['baseline_refold_manifest_sha256'] or bd['refolded_sha256']!=sha(Path(c['baseline_refold_manifest']).parent/'refolded.h5') or Path(c['baseline_refold_manifest']).parent.name!=spec['baseline_assay']:raise ValueError('Changed reused budgets')
    if any(c[k]!=bc[k] for k in TEACHER_KEYS) or (c['expected_backbones'],len(c['entries']),c['num_sequences'],c['temperature'],c['mpnn_seed'],c['allocation_minutes'],c['work_cap_seconds'])!=(16,16,8,.1,1,20,1110) or not c['teacher_deterministic_algorithms'] or c['mpnn_mode']!='ca':raise ValueError('Changed matched design or resource recipe')
    with h5py.File(c['predictions'],locking=False) as inp,h5py.File(gc['fragments'],locking=False) as fr,h5py.File(c['generated_predictions'],locking=False) as gen:
        expected=[]
        for row in gc['selected']:
            ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center']
            if not np.array_equal(inp['motifs/'+ident][:],q['fragment'][:]):raise ValueError('Changed original motif')
            for k in range(4):
                e=make_entry(row,q,k,len(expected),arm='guided');expected.append(e)
                if not np.array_equal(inp[e['dataset']][:],gen['guided/'+ident+'/backbone'][k][None]):raise ValueError('Changed generated candidate')
        if expected!=c['entries'] or set(inp)!={'motifs',*(e['dataset'] for e in expected)}:raise ValueError('Filtered candidate set')
    baseline=[r for r in bd['records'] if r['arm']=='baseline']
    wanted={(r['id'],k) for r in gc['selected'] for k in range(4)}
    if {(r['target_id'],r['generation_slot']) for r in baseline}!=wanted or len(baseline)!=16:raise ValueError('Unpaired reused baseline')
    validate_pairing(c['entries'],baseline)
    if sha(bc['predictions'])!=bc['predictions_sha256']:raise ValueError('Changed reused original query archive')
    with h5py.File(c['predictions'],locking=False) as new,h5py.File(bc['predictions'],locking=False) as old:
        if any(not np.array_equal(new['motifs/'+r['id']][:],old['motifs/'+r['id']][:]) for r in gc['selected']):raise ValueError('Original baseline query geometry differs')
    return dict(sequence_guidance_refold=True),spec


def add_summary(result,c,spec):
    old=json.loads(Path(c['baseline_refold_report']).read_text());reused=[r for r in old['records'] if r['arm'] in ('native','baseline')]
    paired=dict(records=result['records']+reused);paired_summary(paired,spec)
    result.update(sequence_guidance_refold=True,summary=paired['summary'],qualified=paired['qualified'],advancement_gates=paired['advancement_gates'],reused_baseline_report_sha256=c['baseline_refold_report_sha256'],reused_baseline_records=reused)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/sequence_guidance_refold_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['generation'];gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];base=root/'runs'/spec['baseline_assay'];bc=json.loads((base/'manifest.json').read_text())['config'];c={k:bc[k] for k in TEACHER_KEYS}
    c.update(assay='fragment_preference_refold',sequence_guidance_refold=True,partition=0,expected_backbones=16,entries=[],sources=[],allocation_minutes=20,work_cap_seconds=1110,teacher_deterministic_algorithms=True,mpnn_mode='ca');inputs=a.output.with_suffix('.h5').resolve()
    with h5py.File(inputs,'x') as out,h5py.File(gc['fragments'],locking=False) as fr,h5py.File(run/'predictions.h5',locking=False) as gen:
        for row in gc['selected']:
            ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center'];out['motifs/'+ident]=q['fragment'][:]
            for k in range(4):
                e=make_entry(row,q,k,len(c['entries']),arm='guided');c['entries'].append(e);out[e['dataset']]=gen['guided/'+ident+'/backbone'][k][None]
    for key,pth in [('generation_manifest',run/'manifest.json'),('generation_report',root/'reports'/(run.name+'.json')),('generated_predictions',run/'predictions.h5'),('baseline_refold_manifest',base/'manifest.json'),('baseline_refold_report',root/'reports'/(base.name+'.json')),('protocol',protocol),('predictions',inputs)]:
        c[key]=str(pth.resolve());c[key+'_sha256']=sha(pth);c['sources'].append(dict(path=c[key],sha256=c[key+'_sha256']))
    c['sources']+=gc['sources']+c['dependencies']+c['teacher_artifacts'];c['file_identity']=[identity(r['path']) for r in c['sources']];c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit_refold(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('16newbackbones,128refolds;20baseline/native budgets reused unchanged')

if __name__=='__main__':main()
