"""One fixed mid-flow decoder-gradient schedule on four paired diagnostic queries."""
import argparse,json,tempfile,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae_decoder_only
from latentfold.flow import target_noise
from latentfold.fragment_conditioning import sample_fragment
from latentfold.fragment_cross_attention import load_fragment_adapter
from latentfold.endpoint_guidance import proper_loss
from latentfold.trajectory_guidance import sample
from latentfold.precision import inference_precision
from latentfold.training_subset import frozen_digest
from latentfold.metrics import ca_metrics
from fragment_validation_core import raw_rows
from extra_fragment_validation_core import load_conditions
from context_flow_generation import audit_worker
from local_checkpoint import stage_checkpoint
from prepare_overfit import sha
from profile_gpu import atomic_json,Telemetry


def main():
    p=argparse.ArgumentParser()
    for k in ('config','output','source'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());audit_worker(c);spec=c['spec'];a.output.mkdir(exist_ok=False)
    tick=time.monotonic();m=dict(status='running',config=c,controls=[],batches=[]);atomic_json(a.output/'manifest.json',m);telemetry=None
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);telemetry=Telemetry(a.output,True)
        with tempfile.TemporaryDirectory(prefix='trajectory_guidance_') as tmp:
            staged=stage_checkpoint(c['checkpoint'],c['sources'],Path(tmp)/'generator')
            net,_=load_legacy(staged,trusted_pickle=True);net.cuda().eval().requires_grad_(False)
            ck=torch.load(staged,map_location='cpu',weights_only=False,mmap=True);adapter=load_fragment_adapter(ck,net).cuda().eval().requires_grad_(False);del ck
        decoder=load_proteinae_decoder_only(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        models=dict(generator=net,adapter=adapter,decoder=decoder);m['weights_before']={k:frozen_digest(v) for k,v in models.items()}
        conditions=load_conditions(c['fragments'],[r['id'] for r in c['selected']],'c20_center',cohort='train')
        with inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out,h5py.File(c['parent_predictions'],locking=False) as old:
            for ident,item in conditions.items():
                if time.monotonic()-tick>spec['work_cap_seconds']:raise TimeoutError('Pilot work cap')
                n=item['length'];features=item['features'][None].expand(4,-1,-1).cuda();keep=item['keep'][None].expand(4,-1).cuda();coords=item['coordinates'][None].expand(4,-1,-1).cuda();mask=torch.ones(4,n,dtype=torch.bool,device='cuda')
                noise=torch.cat([target_noise([ident],[n],8,seed=spec['seed'],sample_index=k,stream='flow:0',device='cuda') for k in range(4)])
                dn=torch.cat([target_noise([ident],[4*n],3,seed=spec['seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                fragment=torch.from_numpy(item['fragment']).cuda();st=item['start'];control=dict(target_id=ident);m['controls'].append(control)
                def objective(z,query=fragment):
                    _,bb=decoder(z,mask,noise=dn,return_backbone=True)
                    return proper_loss(bb,query,st)
                def derivative_check(current,estimate,loss_fn,ad_loss,gradient):
                    with torch.no_grad():
                        loss=loss_fn(estimate(current)[1]);err=float((loss-ad_loss).abs().max())
                    norm=gradient[0].norm()
                    if not torch.isfinite(gradient).all() or norm<=1e-10:raise ValueError('Missing actual gradient')
                    direction=torch.zeros_like(gradient);direction[0]=gradient[0]/norm;analytic=float((gradient*direction).sum());fd=[]
                    with torch.no_grad():
                        for eps in (.01,.001):
                            numeric=float((loss_fn(estimate(current+eps*direction)[1])[0]-loss_fn(estimate(current-eps*direction)[1])[0])/(2*eps));fd.append(dict(epsilon=eps,numeric=numeric,analytic=analytic,passed=abs(numeric-analytic)<=max(.01,.05*abs(analytic))))
                    rotation=fragment.new_tensor([[0,-1,0],[1,0,0],[0,0,1]]);posed=fragment@rotation+fragment.new_tensor([11,7,-3])
                    with torch.enable_grad():
                        probe=current.detach().requires_grad_();posed_loss=objective(estimate(probe)[1],posed);pg,=torch.autograd.grad(posed_loss.sum(),probe)
                    pose_error=float((pg-gradient).norm()/gradient.norm().clamp_min(1e-12));control.update(ad_loss_error=err,finite_differences=fd,finite_difference_passed=any(r['passed'] for r in fd),pose_gradient_relative_error=pose_error)
                    atomic_json(a.output/'manifest.json',m)
                    if err>.001 or pose_error>1e-4 or not control['finite_difference_passed']:raise ValueError('Derivative control failed')
                with torch.no_grad():canonical=sample_fragment(net,adapter,features,keep,mask,noise=noise,steps=50,coordinates=coords)
                for arm,strength in [('baseline',0.),('guided',spec['strength'])]:
                    g=out.create_group(arm+'/'+ident);states=g.create_group('states');io=[0.]
                    def observe(i,x,v,direction,following,loss,weight,t,dt):
                        start=time.monotonic();s=states.create_group(str(i))
                        for key,val in [('x',x),('v',v),('direction',direction),('next',following)]:s[key]=val.cpu().numpy()
                        if loss is not None:s['loss']=loss.cpu().numpy()
                        s.attrs.update(weight=weight,t=t,dt=dt);io[0]+=time.monotonic()-start
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();begin=time.monotonic()
                    z=sample(net,adapter,features,keep,mask,noise=noise,coordinates=coords,objective=objective,strength=strength,first=spec['first'],stop=spec['stop'],observe=observe,derivative_check=derivative_check if strength else None)
                    with torch.no_grad():_,bb=decoder(z,mask,noise=dn,return_backbone=True)
                    torch.cuda.synchronize();seconds=time.monotonic()-begin;peak=torch.cuda.max_memory_reserved()/2**30
                    if peak>75:raise ValueError('Memory limit exceeded')
                    zn=z.cpu().numpy();bn=bb.cpu().numpy();g['latent']=zn;g['backbone']=bn
                    m['batches'].append(dict(arm=arm,target_id=ident,samples=4,length=n,seconds=seconds,recording_seconds=io[0],peak_reserved_GiB=peak))
                    if arm=='baseline':
                        reference=old['new/'+ident];rb=reference['backbone'][:];scores=[ca_metrics(x[:,1],y[:,1]) for x,y in zip(bn,rb)];left=raw_rows(bn,item['fragment'],st,arm,ident,item['family']);right=raw_rows(rb,item['fragment'],st,arm,ident,item['family'])
                        control.update(zero_max_abs=float((z-canonical).abs().max()),historical_latent_max_abs=float(np.max(abs(zn-reference['latent'][:]))),historical_max_ca_rmsd=max(r['ca_rmsd'] for r in scores),historical_min_lddt=min(r['ca_lddt'] for r in scores),same_decisions=all(x[k]==y[k] for x,y in zip(left,right) for k in ('coarse_valid','raw_gate_passed')))
                        atomic_json(a.output/'manifest.json',m)
                        if control['zero_max_abs']!=0 or control['historical_latent_max_abs']>1e-5 or control['historical_max_ca_rmsd']>.2 or control['historical_min_lddt']<.99 or not control['same_decisions']:raise ValueError('Historical replay failed')
                    out.flush();atomic_json(a.output/'manifest.json',m)
                    print(ident,arm,round(seconds,3),'seconds',round(peak,3),'GiB',flush=True)
                del canonical,z,bb
        m['weights_after']={k:frozen_digest(v) for k,v in models.items()}
        if m['weights_before']!=m['weights_after']:raise ValueError('Frozen weights changed')
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as e:m.update(status='failed',error=f'{type(e).__name__}: {e}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
