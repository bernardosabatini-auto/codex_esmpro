"""Profile a bounded local decoder correction, retaining every proposal."""
import argparse,json,time,traceback
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.precision import inference_precision
from latentfold.endpoint_guidance import retract,tangent_gradient,proper_loss
from latentfold.noise_guidance import normalized_gradient
from latentfold.metrics import ca_metrics
from fragment_endpoint_core import audit_config,score
from profile_gpu import atomic_json
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec=audit_config(c,decoder=True);a.output.mkdir(parents=True,exist_ok=False);m=dict(status='running',config=c,controls=[],cases=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m);start_time=time.monotonic()
    try:
        torch.set_num_threads(1);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        if any(p.requires_grad for p in decoder.parameters()):raise ValueError('Trainable decoder')
        with inference_precision('fp32'),h5py.File(c['parent_predictions']) as parent,h5py.File(c['fragments']) as fragments,h5py.File(a.output/'predictions.h5','x') as out:
            for ident in c['target_ids']:
                if time.monotonic()-start_time>spec['work_cap_seconds']:raise TimeoutError('Correction work cap')
                q=fragments['development/'+ident+'/conditions/f30_center'];fragment=q['fragment'][:];st=int(q.attrs['start']);source=parent[spec.get('prediction_prefix','development/conditioned')+'/'+ident];z0=torch.from_numpy(source['latent'][:4]).cuda();n=z0.shape[1];mask=torch.ones(4,n,dtype=torch.bool,device='cuda');ref=torch.from_numpy(fragment).cuda();noise=torch.cat([target_noise([ident],[4*n],3,seed=spec['generation_seed'],sample_index=k,stream='decoder:0',device='cuda') for k in range(4)])*decoder.fm.scale_ref
                if z0.shape!=(4,n,8):raise ValueError('Changed cached batch')
                group=out.create_group(ident);group.attrs.update(start=st,sequence=str(q.attrs['sequence']),family=str(fragments['development/'+ident].attrs['family']));group.create_dataset('fragment',data=fragment);group.create_dataset('initial_latent',data=z0.cpu().numpy())
                def decode(z):
                    _,bb=decoder(z,mask,noise=noise,return_backbone=True)
                    return proper_loss(bb,ref,st),bb
                with torch.no_grad():initial_loss,initial_bb=decode(z0)
                initial=initial_bb.cpu().numpy();expected=source['backbone'][:4];old=score(expected,fragment,st);current_scores=score(initial,fragment,st)
                for k in range(4):
                    metrics=ca_metrics(initial[k,:,1],expected[k,:,1]);passed=metrics['ca_rmsd']<=.2 and metrics['ca_lddt']>=.99 and old[k]['coarse_valid']==current_scores[k]['coarse_valid'] and old[k]['raw_gate_passed']==current_scores[k]['raw_gate_passed'];m['controls'].append(dict(kind='historical',target_id=ident,slot=k,passed=passed,**metrics))
                    if not passed:raise ValueError('Historical redecoding changed')
                group.create_dataset('initial_backbone',data=initial);group.create_dataset('initial_loss',data=initial_loss.cpu().numpy())
                x=z0.clone().requires_grad_();loss,bb=decode(x);metric=ca_metrics(bb[0,:,1].detach().cpu().numpy(),initial[0,:,1]);passed=metric['ca_rmsd']<=.01 and metric['ca_lddt']>=.999;m['controls'].append(dict(kind='autograd_forward',target_id=ident,passed=passed,**metric))
                if not passed:raise ValueError('Autograd forward changed')
                gradient,=torch.autograd.grad(loss[0],x);direction=tangent_gradient(gradient,z0);norm=direction.norm()
                if not torch.isfinite(direction).all() or norm<=1e-10:raise ValueError('Missing finite tangent gradient')
                direction=direction/norm;analytic=float((gradient*direction).sum());checks=[]
                with torch.no_grad():
                    for eps in spec['finite_difference_eps']:
                        plus=decode(retract(z0+eps*direction,z0))[0][0];minus=decode(retract(z0-eps*direction,z0))[0][0];fd=float((plus-minus)/(2*eps));checks.append(dict(eps=eps,derivative=fd,absolute_error=abs(fd-analytic)))
                passed=any(r['absolute_error']<=max(.01,.05*abs(analytic)) for r in checks);m['controls'].append(dict(kind='finite_difference',target_id=ident,analytic=analytic,checks=checks,passed=passed));atomic_json(a.output/'manifest.json',m)
                if not passed:raise ValueError('Decoder tangent derivative failed')
                del x,loss,bb,gradient,direction
                current=z0.clone();current_loss=initial_loss.detach();current_bb=initial_bb.detach();scale=z0.square().mean((1,2)).sqrt();updates=group.create_group('updates');torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();gradient_calls=0;proposal_calls=0
                for update in range(spec['max_updates']):
                    if time.monotonic()-start_time>spec['work_cap_seconds']:raise TimeoutError('Correction work cap')
                    active=(2*current_loss).sqrt()>spec['desired_rmsd']
                    if not active.any():break
                    x=current.detach().requires_grad_();loss,_=decode(x);gradient,=torch.autograd.grad(loss[active].sum(),x);direction=normalized_gradient(tangent_gradient(gradient,current),mask).detach();gradient_calls+=1;ug=updates.create_group(str(update));ug.create_dataset('direction',data=direction.cpu().numpy());base=current.clone();remaining=active.clone();accepted_this_update=torch.zeros_like(active)
                    for line,step in enumerate(spec['line_search_steps']):
                        if not remaining.any():break
                        with torch.no_grad():
                            proposal=retract(base-step*scale[:,None,None]*direction,z0);displacement=(proposal-z0).square().mean((1,2)).sqrt()/scale;ploss,pbb=decode(proposal);accepted=remaining&(displacement<=spec['relative_radius'])&(ploss<current_loss);proposal_calls+=1
                            if spec.get('validity_guarded'):
                                valid=torch.tensor([r['coarse_valid'] for r in score(pbb.cpu().numpy(),fragment,st)],device=accepted.device);accepted &= valid
                        pg=ug.create_group(str(line));pg.attrs['step']=step
                        for name,value in [('latent',proposal),('backbone',pbb),('loss',ploss),('relative_displacement',displacement),('accepted',accepted)]:pg.create_dataset(name,data=value.detach().cpu().numpy())
                        current=torch.where(accepted[:,None,None],proposal,current).detach();current_bb=torch.where(accepted[:,None,None,None],pbb,current_bb).detach();current_loss=torch.where(accepted,ploss,current_loss).detach();remaining=remaining&~accepted;accepted_this_update |= accepted
                    del x,loss,gradient,direction
                    if not accepted_this_update.any():break
                torch.cuda.synchronize();seconds=time.monotonic()-tick;peak=torch.cuda.max_memory_reserved()
                if peak/2**30>75:raise ValueError('Correction memory cap')
                group.create_dataset('guided_latent',data=current.cpu().numpy());group.create_dataset('guided_backbone',data=current_bb.cpu().numpy());group.create_dataset('guided_loss',data=current_loss.cpu().numpy());out.flush();m['cases'].append(dict(target_id=ident,seconds=seconds,gradient_calls=gradient_calls,proposal_calls=proposal_calls,peak_reserved_bytes=peak));atomic_json(a.output/'manifest.json',m);print(ident,'correction seconds',round(seconds,3),flush=True)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except Exception as error:
        m.update(status='failed',error=type(error).__name__+': '+str(error),traceback=traceback.format_exc());raise
    finally:
        m['elapsed_seconds']=time.monotonic()-start_time;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
