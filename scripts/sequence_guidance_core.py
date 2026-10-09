"""Bind the sequence-compatible objective to the unchanged paired flow pilot."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np,torch
from context_flow_generation import identity
from trajectory_guidance_core import audit,analyze as geometric_analysis
from latentfold.motif_sequence_score import load_model,motif_nll
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def prepare(root,output):
    protocol=root/'configs/sequence_guidance_protocol.json';spec=json.loads(protocol.read_text());gm=root/'runs'/spec['geometry_generation']/'manifest.json';m=json.loads(gm.read_text());c=m['config'].copy();c.pop('config_sha256');c['spec']=spec;c['sources']=[r for r in c['sources'] if r['path']!=c['protocol']];c['protocol']=str(protocol.resolve())
    cr=root/spec['compatibility_report'];d=json.loads(cr.read_text())
    if d['status']!='complete' or d['mode']!='backbone' or not d['gradient_qualified'] or len(d['controls'])!=4:raise ValueError('Unqualified sequence objective')
    utils=next(Path(r['path']) for r in d['sources'] if r['path'].endswith('protein_mpnn_utils.py'));weights=next(Path(r['path']) for r in d['sources'] if r['path'].endswith('v_48_020.pt'))
    for key,pth in [('protocol',protocol),('compatibility_report',cr),('geometry_manifest',gm),('geometry_predictions',gm.parent/'predictions.h5'),('sequence_utils',utils),('sequence_weights',weights),('sequence_source',root/'src/latentfold/motif_sequence_score.py')]:
        c[key]=str(pth.resolve());c['sources'].append(dict(path=c[key],sha256=sha(pth)))
    if any(sha(r['path'])!=r['sha256'] for r in d['sources'] if r['path'] in (str(utils),str(weights))):raise ValueError('Changed qualified sequence model')
    c['file_identity']=[identity(r['path']) for r in c['sources']];c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit(c);output.write_text(json.dumps(c,indent=2)+'\n')


def analyze(run):
    result=geometric_analysis(run);m=json.loads((run/'manifest.json').read_text());c=m['config'];spec=c['spec']
    if not spec.get('joint_sequence_guidance'):raise ValueError('Wrong objective')
    for control in m['controls']:
        if control['geometry_replay_max_abs']!=0 or control['sequence_pose_error']>1e-4:raise ValueError('Sequence/geometry control failed')
    model=load_model(c['sequence_utils'],c['sequence_weights']);conditions=load_conditions(c['fragments'],[r['id'] for r in c['selected']],'c20_center',cohort='train');scores=[]
    with torch.no_grad(),h5py.File(run/'predictions.h5',locking=False) as f,h5py.File(c['geometry_predictions'],locking=False) as old,h5py.File(c['fragments'],locking=False) as fr:
        for row in c['selected']:
            ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center'];seq=str(q.attrs['sequence']);st=int(q.attrs['start'])
            for arm,bb in [('geometry',old['guided/'+ident+'/backbone'][:]),('baseline',f['baseline/'+ident+'/backbone'][:]),('guided',f['guided/'+ident+'/backbone'][:])]:
                nll=motif_nll(model,torch.from_numpy(bb),seq,st).numpy()
                if arm!='geometry' and np.max(abs(nll-f[arm+'/'+ident+'/motif_nll'][:]))>1e-4:raise ValueError('CPU/GPU sequence score mismatch')
                scores.extend(dict(arm=arm,target_id=ident,slot=k,nll=float(v)) for k,v in enumerate(nll))
    means={arm:float(np.mean([r['nll'] for r in scores if r['arm']==arm])) for arm in ('geometry','baseline','guided')}
    improvement=means['geometry']-means['guided'];result.update(joint_sequence_guidance=True,geometry_gate_passed=result['qualified'],sequence_nll=means,sequence_nll_improvement=improvement,sequence_scores=scores,qualified=result['qualified'] and improvement>=spec['minimum_nll_improvement'])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();prepare(Path(__file__).resolve().parents[1],a.output)
