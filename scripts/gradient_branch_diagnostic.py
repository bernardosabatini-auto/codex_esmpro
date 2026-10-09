"""Differentiate the failed joint objective with dynamic and fixed neighbor lists."""
import argparse,hashlib,json,tempfile,time
from pathlib import Path
import h5py,numpy as np,torch
from torch.nn import functional as F
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae_decoder_only
from latentfold.fragment_cross_attention import load_fragment_adapter
from latentfold.fragment_conditioning import prepare_fragment_condition,fragment_velocity
from latentfold.flow import target_noise
from latentfold.endpoint_guidance import proper_loss
from latentfold.motif_sequence_score import load_model,motif_nll
from latentfold.precision import inference_precision
from latentfold.training_subset import frozen_digest
from extra_fragment_validation_core import load_conditions
from context_flow_generation import identity,audit_worker
from verified_sources import VerifiedSources
from local_checkpoint import stage_checkpoint
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def prepare(root,output):
    protocol=root/'configs/gradient_branch_diagnostic_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['failed_run'];m=json.loads((run/'manifest.json').read_text());c=m['config'].copy();c.pop('config_sha256');c['sources']=[r for r in c['sources'] if r['path']!=c['protocol']];c['spec']=spec
    if m['status']!='failed' or m.get('error')!='ValueError: Derivative control failed' or len(m['controls'])!=1:raise ValueError('Wrong failed numerical control')
    for key,p in [('protocol',protocol),('failed_manifest',run/'manifest.json'),('failed_predictions',run/'predictions.h5')]:
        c[key]=str(p.resolve());c['sources'].append(dict(path=c[key],sha256=sha(p)))
    verifier=VerifiedSources()
    for r in c['sources']:verifier.verify(r)
    c['file_identity']=[identity(r['path']) for r in c['sources']];c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();audit_worker(c);output.write_text(json.dumps(c,indent=2)+'\n')


def execute(a):
    c=json.loads(a.config.read_text());audit_worker(c);spec=c['spec'];a.output.mkdir(exist_ok=False);tick=time.monotonic();m=dict(status='running',config=c);atomic_json(a.output/'manifest.json',m);telemetry=None
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);telemetry=Telemetry(a.output,True)
        with tempfile.TemporaryDirectory(prefix='joint_gradient_diagnostic_') as tmp:
            staged=stage_checkpoint(c['checkpoint'],c['sources'],Path(tmp)/'generator');net,_=load_legacy(staged,trusted_pickle=True);net.cuda().eval().requires_grad_(False);ck=torch.load(staged,map_location='cpu',weights_only=False,mmap=True);adapter=load_fragment_adapter(ck,net).cuda().eval().requires_grad_(False);del ck
        decoder=load_proteinae_decoder_only(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);mpnn=load_model(c['sequence_utils'],c['sequence_weights']).cuda().eval().requires_grad_(False);models=dict(net=net,adapter=adapter,decoder=decoder,sequence_model=mpnn);m['weights_before']={k:frozen_digest(v) for k,v in models.items()}
        failed=json.loads(Path(c['failed_manifest']).read_text());ident=c['selected'][0]['id'];item=load_conditions(c['fragments'],[ident],'c20_center',cohort='train')[ident];n=item['length'];st=item['start'];features=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda();mask=torch.ones(4,n,dtype=torch.bool,device='cuda');fragment=torch.from_numpy(item['fragment']).cuda()
        with h5py.File(c['geometry_predictions'],locking=False) as old,h5py.File(c['failed_predictions'],locking=False) as bad,h5py.File(c['fragments'],locking=False) as fr:
            seq=str(fr['train/'+ident+'/conditions/c20_center'].attrs['sequence']);g=old['guided/'+ident+'/states'];x=torch.from_numpy(g['25/x'][:]).cuda();history=torch.from_numpy(g['24/x'][:]).cuda()+(1-float(g['24'].attrs['t']))*torch.from_numpy(g['24/v'][:]).cuda();expected_v=torch.from_numpy(g['25/v'][:]).cuda();expected_geometry=g['25/loss'][:]
            if not np.array_equal(x.cpu().numpy(),bad['guided/'+ident+'/states/24/next'][:]):raise ValueError('Failed and archived states differ')
        dn=torch.cat([target_noise([ident],[4*n],3,seed=failed['config']['spec']['seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
        with torch.no_grad(),inference_precision('fp32'):esm,prepared=prepare_fragment_condition(net,adapter,features,keep,mask,torch.zeros(4,dtype=torch.bool,device='cuda'),coordinates=coords)
        original=mpnn.features._dist;state=dict(mode='dynamic',indices=None,last=None)
        def distances(points,valid,eps=1e-6):
            if state['mode']=='dynamic':
                values,indices=original(points,valid,eps);state['last']=indices.detach().clone();return values,indices
            indices=state['indices'];mask2=valid[:,:,None]*valid[:,None,:];delta=points[:,:,None]-points[:,None,:];d=mask2*torch.sqrt(delta.square().sum(-1)+eps);adjusted=d+(1-mask2)*d.max(-1,keepdim=True).values;state['last']=indices.detach().clone();return torch.gather(adjusted,2,indices),indices
        mpnn.features._dist=distances
        def evaluate(current):
            v=fragment_velocity(net,adapter,current,current.new_full((4,),.5),esm,mask,x_sc=history,prepared=prepared).float();z=F.layer_norm(current+.5*v,(8,));_,bb=decoder(z,mask,noise=dn,return_backbone=True);losses=torch.stack((proper_loss(bb,fragment,st),motif_nll(mpnn,bb,seq,st)),1);return losses,bb,v
        with inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            current=x.clone().requires_grad_();losses,bb,v=evaluate(current);gradient,=torch.autograd.grad(losses.sum(),current);indices=state['last'];direction=torch.zeros_like(gradient);direction[0]=gradient[0]/gradient[0].norm();analytic=float((gradient*direction).sum());reference_loss=losses.detach();state['indices']=indices
            controls=dict(velocity_max_abs=float((v-expected_v).abs().max()),geometry_loss_max_abs=float(np.max(abs(losses[:,0].detach().cpu().numpy()-expected_geometry))),failed_analytic_error=abs(analytic-failed['controls'][0]['finite_differences'][0]['analytic']))
            if controls['velocity_max_abs']!=0 or controls['geometry_loss_max_abs']>1e-8 or controls['failed_analytic_error']>1e-6:raise ValueError('Failed point did not reproduce')
            out['x']=x.cpu().numpy();out['direction']=direction.cpu().numpy();out['reference_neighbors']=indices.cpu().numpy();out['reference_losses']=reference_loss.cpu().numpy();rows=[]
            for mode in ('dynamic','fixed'):
                state['mode']=mode
                current=x.clone().requires_grad_();base,_,_=evaluate(current);check_grad,=torch.autograd.grad(base.sum(),current);grad_error=float((check_grad-gradient).abs().max());forward_error=float((base-reference_loss).abs().max())
                controls[mode]=dict(reference_loss_max_abs=forward_error,gradient_max_abs=grad_error)
                if forward_error>1e-8 or grad_error>1e-6:raise ValueError('Fixed branch changed reference computation')
                for eps in spec['epsilons']:
                    values=[];changes=[]
                    for sign in (-1,1):
                        with torch.no_grad():ls,backbone,_=evaluate(x+sign*eps*direction)
                        idx=state['last'];changes.append(int((idx[0].sort(-1).values!=indices[0].sort(-1).values).any(-1).sum()));values.append(ls)
                        prefix=f'{mode}/{eps}/{sign}';out[prefix+'/losses']=ls.cpu().numpy();out[prefix+'/neighbors']=idx.cpu().numpy();out[prefix+'/backbone']=backbone.cpu().numpy()
                    components=((values[1]-values[0])[0]/(2*eps)).cpu().numpy();numeric=float(components.sum());rows.append(dict(mode=mode,epsilon=eps,analytic=analytic,numeric=numeric,components=components.tolist(),changed_neighbor_rows=changes,passed=abs(numeric-analytic)<=max(.01,.05*abs(analytic))))
                print(mode,rows[-len(spec['epsilons']):],flush=True)
            m.update(controls=controls,rows=rows)
        m['weights_after']={k:frozen_digest(v) for k,v in models.items()}
        if m['weights_before']!=m['weights_after']:raise ValueError('Frozen weights changed')
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'),peak_reserved_GiB=torch.cuda.max_memory_reserved()/2**30)
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


def analyze(run):
    m=json.loads((run/'manifest.json').read_text());c=m['config'];audit_worker(c)
    if m['status']!='complete' or m['weights_before']!=m['weights_after'] or m['predictions_sha256']!=sha(run/'predictions.h5'):raise ValueError('Incomplete diagnostic')
    with h5py.File(run/'predictions.h5',locking=False) as f:
        ref=f['reference_neighbors'][:]
        for r in m['rows']:
            prefix=f'{r["mode"]}/{r["epsilon"]}';components=(f[prefix+'/1/losses'][0]-f[prefix+'/-1/losses'][0])/(2*r['epsilon'])
            if not np.allclose(components,np.array(r['components']),rtol=1e-10,atol=1e-10):raise ValueError('Changed derivative arithmetic')
            changes=[int(np.any(np.sort(f[prefix+'/'+str(sign)+'/neighbors'][0],axis=-1)!=np.sort(ref[0],axis=-1),axis=-1).sum()) for sign in (-1,1)]
            if changes!=r['changed_neighbor_rows']:raise ValueError('Changed neighbor branch evidence')
    return dict(status='complete',gradient_branch_diagnostic=True,scientific_candidates=0,controls=m['controls'],rows=m['rows'],elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],manifest_sha256=sha(run/'manifest.json'),predictions_sha256=m['predictions_sha256'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--config',type=Path);p.add_argument('--source',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.prepare:prepare(Path(__file__).resolve().parents[1],a.output)
    else:execute(a)
