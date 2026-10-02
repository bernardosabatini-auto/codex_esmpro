"""Motif-only guidance from frozen best random starts, with no latent-code insertion."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.generative import sample_unconditional
from latentfold.motif_objective import motif_distance_mse
from latentfold.noise_guidance import unconditional_endpoint,normalized_gradient,project_radius
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','parent_manifest','parent_predictions','selection','checkpoint','decoder_checkpoint','fragment_manifest','fragment_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    rows={r['target_id']:r for r in json.loads(Path(c['selection']).read_text())['rows']}
    if c['samples']!=2 or len(c['target_ids'])!=4 or c['steps']!=50 or c['max_updates']!=12 or c['line_search_steps']!=[.05,.025,.0125,.00625] or c['random_samples']!=32:raise ValueError('Changed profile recipe')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,cases=[],controls=[],proposals=[],iterations=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);model.checkpoint_blocks=False;decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False);telemetry=Telemetry(a.output,True)
        with inference_precision('fp32'),h5py.File(c['parent_predictions']) as parent,h5py.File(c['fragment_predictions']) as fragments,h5py.File(a.output/'predictions.h5','x') as f:
            for ident in c['target_ids']:
                n=rows[ident]['length'];fragment=torch.from_numpy(fragments[ident+'/fragment'][:]).cuda();fragment_start=(n-len(fragment))//2;mask=torch.ones(1,n,dtype=torch.bool,device='cuda')
                for slot in range(c['samples']):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Noise guidance cap')
                    tag=f'{ident}/{slot}';group=f.create_group(tag);choice=next(r for r in c['choices'] if (r['target_id'],r['slot'])==(ident,slot));index=choice['index'];initial=target_noise([ident],[n],8,seed=c['generation_seed'] if index==0 else c['search_seed'],sample_index=slot if index==0 else index-1,stream='flow:0' if index==0 else f'flow_search:{slot}',device='cuda');dn=target_noise([ident],[4*n],3,seed=c['generation_seed'],sample_index=slot,stream='decoder:0',device='cuda')*decoder.fm.scale_ref
                    def generate(x,checkpoint_steps=True):
                        z=unconditional_endpoint(model,x,mask.expand(len(x),-1),steps=50,checkpoint_steps=checkpoint_steps);_,bb=decoder(z,mask.expand(len(x),-1),noise=dn.expand(len(x),-1,-1),return_backbone=True);mse=motif_distance_mse(bb,fragment,fragment_start);d=mse.clamp_min(1e-12).sqrt();return .5*mse,d,bb,z
                    with torch.no_grad():
                        torch.cuda.synchronize();initial_tick=time.monotonic();obj,dist,bb,z=generate(initial);torch.cuda.synchronize();initial_seconds=time.monotonic()-initial_tick;generic=sample_unconditional(model,torch.zeros(1,n,2560,device='cuda'),mask,noise=initial,steps=50);expected=parent[tag+'/random_all'][index];valid=bool(backbone_geometry(bb.cpu().numpy())['coarse_valid'][0]);control=dict(target_id=ident,slot=slot,latent_max_abs=float((z-generic).abs().max()),validity_identical=valid==bool(backbone_geometry(expected[None])['coarse_valid'][0]),**ca_metrics(bb[0,:,1].cpu().numpy(),expected[:,1]));m['controls'].append(dict(kind='forward',**control));atomic_json(a.output/'manifest.json',m)
                        if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.2 or control['ca_lddt']<.99 or not control['validity_identical']:raise ValueError('Initial forward identity failed')
                        initial_bb=bb.detach().clone();initial_distance=float(dist[0]);group.create_dataset('initial',data=bb[0].cpu().numpy());group.create_dataset('initial_noise',data=initial[0].cpu().numpy())
                    if slot==0:
                        x=initial.clone().requires_grad_();loss,_,ad_bb,ad_z=generate(x);control=dict(kind='ad_forward',target_id=ident,latent_max_abs=float((ad_z-z).abs().max().detach()),**ca_metrics(ad_bb[0,:,1].detach().cpu().numpy(),initial_bb[0,:,1].cpu().numpy()));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                        if control['latent_max_abs']>1e-5 or control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Autograd forward differs from sampling')
                        gradient,=torch.autograd.grad(loss.sum(),x);norm=gradient.norm()
                        if not torch.isfinite(gradient).all() or norm<=1e-10:raise ValueError('Missing/nonfinite actual gradient')
                        direction=gradient/norm;analytic=float((gradient*direction).sum());checks=[]
                        with torch.no_grad():
                            for eps in c['finite_difference_eps']:
                                plus=generate(initial+eps*direction)[0];minus=generate(initial-eps*direction)[0];fd=float((plus-minus)/(2*eps));checks.append(dict(eps=eps,derivative=fd,absolute_error=abs(fd-analytic)))
                        control=dict(kind='finite_difference',target_id=ident,slot=slot,analytic=analytic,checks=checks,passed=any(r['absolute_error']<=max(.01,.05*abs(analytic)) for r in checks));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                        if not control['passed']:raise ValueError('Actual decoder/flow finite differences failed')
                        if ident==c['target_ids'][0]:
                            direct=initial.clone().requires_grad_();dloss,_,_,_=generate(direct,False);dg,=torch.autograd.grad(dloss.sum(),direct);error=float((gradient-dg).norm()/gradient.norm().clamp_min(1e-12));control=dict(kind='gradient_checkpoint',target_id=ident,relative_l2=error);m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                            if error>1e-4:raise ValueError('Gradient checkpoint identity failed')
                            del direct,dloss,dg
                        del x,loss,gradient,direction,ad_bb,ad_z
                    current=initial.clone();accepted_bb=initial_bb.clone();current_distance=initial_distance;current_loss=.5*current_distance**2;gradients=0;proposal_count=0;io_seconds=0.;torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                    iterates=group.create_group('iterates');proposals=group.create_group('proposals')
                    for update in range(c['max_updates']):
                        if current_distance<=1:break
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Guidance work cap')
                        x=current.detach().requires_grad_();loss,_,_,_=generate(x);g,=torch.autograd.grad(loss.sum(),x);gradients+=1;ng=normalized_gradient(g,mask);accepted=False
                        for trial,alpha in enumerate(c['line_search_steps']):
                            with torch.no_grad():
                                proposed=project_radius(current-alpha*ng,initial,mask);cost,d,proposal_bb,_=generate(proposed);new_loss=float(cost[0]);new_distance=float(d[0]);take=new_loss<=current_loss;proposal_array=proposal_bb[0].cpu().numpy();io_tick=time.monotonic();proposals.create_dataset(str(proposal_count),data=proposal_array);io_seconds+=time.monotonic()-io_tick;m['proposals'].append(dict(target_id=ident,slot=slot,index=proposal_count,update=update,trial=trial,alpha=alpha,loss=new_loss,distance=new_distance,accepted=take));proposal_count+=1
                                if take:current=proposed.detach();current_distance=new_distance;current_loss=new_loss;accepted_bb=proposal_bb.detach();accepted=True;break
                        noise_array=current[0].cpu().numpy();bb_array=accepted_bb[0].cpu().numpy();io_tick=time.monotonic();it=iterates.create_group(str(update));it.create_dataset('noise',data=noise_array);it.create_dataset('backbone',data=bb_array);io_seconds+=time.monotonic()-io_tick;m['iterations'].append(dict(target_id=ident,slot=slot,update=update,accepted=accepted,distance=current_distance,loss=current_loss,radius_relative_error=float((current.norm()-initial.norm()).abs()/initial.norm())));del x,loss,g,ng
                        io_tick=time.monotonic();f.flush();atomic_json(a.output/'manifest.json',m);io_seconds+=time.monotonic()-io_tick
                    torch.cuda.synchronize();guided_seconds=time.monotonic()-tick-io_seconds;guided_peak=torch.cuda.max_memory_reserved();group.create_dataset('guided',data=accepted_bb[0].cpu().numpy());group.create_dataset('guided_noise',data=current[0].cpu().numpy())
                    random=parent[tag+'/random_all'][:];group.create_dataset('random_all',data=random);group.create_dataset('random_selected',data=random[index]);group.attrs['random_selected_index']=index
                    record=dict(target_id=ident,family=rows[ident]['family'],slot=slot,length=n,initial_distance=initial_distance,initial_seconds=choice['search_seconds'],initial_regeneration_seconds=initial_seconds,guided_io_seconds=io_seconds,guided_distance=current_distance,random_distance=choice['motif_drms'],random_selected_index=index,guided_seconds=guided_seconds,random_seconds=0.,gradient_evaluations=gradients,line_search_proposals=proposal_count,guided_peak_GiB=guided_peak/2**30,random_peak_GiB=None)
                    for mode,value in [('initial',initial_bb.cpu().numpy()),('guided',accepted_bb.cpu().numpy()),('random',random[index:index+1])]:record[mode+'_coarse_valid']=bool(backbone_geometry(value)['coarse_valid'][0])
                    m['cases'].append(record);f.flush();atomic_json(a.output/'manifest.json',m);print('guided',ident,slot,record,flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
