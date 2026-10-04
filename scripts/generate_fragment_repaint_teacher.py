"""Generate oracle-label candidates with the original full-context RePaint recipe."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import target_noise
from latentfold.generative import sample_unconditional
from latentfold.precision import inference_precision
from evaluate_decoder_fragment_variance import check_backbones
from fragment_repaint_teacher_core import audit
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def generate(model,decoder,ident,n,start,k,target,seed,*,outside=None):
    mask=torch.ones(4,n,dtype=torch.bool,device='cuda');keep=torch.zeros_like(mask);keep[:,start:start+k]=True
    z=torch.zeros(4,n,8,device='cuda');z[:,start:start+k]=target
    if outside is not None:z=torch.where(keep[...,None],z,outside.expand_as(z))
    def noise(stream,width=8,mult=1):
        return torch.cat([target_noise([ident],[mult*n],width,seed=seed,sample_index=i,stream=stream,device='cuda') for i in range(4)])
    result=sample_unconditional(model,torch.zeros(4,n,2560,device='cuda'),mask,noise=noise('flow:0'),steps=50,
        fixed=(z,keep),motif_noise=noise('motif:0'),repaint=3,fresh_noise=lambda i,j:noise('refinement:'+str(i*2+j)))
    _,bb=decoder(result,mask,noise=noise('decoder:0',3,4)*decoder.fm.scale_ref,return_backbone=True)
    return result.cpu().numpy(),bb.cpu().numpy(),z.cpu().numpy()


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());spec=audit(c);a.output.mkdir(exist_ok=False)
    tick=time.monotonic();telemetry=None;m=dict(status='running',config=c,controls=[],batches=[],training_updates_executed=0)
    atomic_json(a.output/'manifest.json',m)
    try:
        torch.set_num_threads(2);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval().requires_grad_(False)
        telemetry=Telemetry(a.output,True)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'predictions.h5','x') as out:
            hc=json.loads(Path(c['historical_manifest']).read_text())['config'];oldrows=json.loads(Path(c['historical_selection']).read_text())['rows']
            with h5py.File(c['historical_predictions']) as old,h5py.File(c['historical_parent_predictions']) as hp:
                for ident in hc['control_ids']:
                    row=next(r for r in oldrows if r['target_id']==ident);n=row['length'];k=max(8,int(.3*n));st=(n-k)//2
                    z=torch.from_numpy(hp['references/'+ident+'/latent'][st:st+k]).cuda()
                    latent,bb,_=generate(model,decoder,ident,n,st,k,z,hc['seed'])
                    expected=old[ident+'/full_control'][:];fragment=np.asarray(row['reference']['backbone'],np.float32)[st:st+k]
                    check=check_backbones(bb,expected,fragment,st,ident)
                    gap=float(np.max(np.abs(latent-hp['original50/motif_u3/'+ident+'/latent'][:])))
                    if gap>1e-5:raise ValueError('Historical RePaint latent mismatch')
                    g=out.create_group('historical/'+ident);g['latent']=latent;g['backbone']=bb
                    m['controls'].append(dict(kind='historical',target_id=ident,latent_max_abs=gap,**check))
            seen=set()
            with h5py.File(c['fragments']) as fr:
                for row in c['selected']:
                    if time.monotonic()-tick>c['work_cap_seconds']:raise TimeoutError('Oracle teacher cap')
                    ident=row['id'];n=row['length'];q=fr['train/'+ident+'/conditions/c20_center'];st=int(q.attrs['start'])
                    codes=torch.from_numpy(fr['train/'+ident+'/reference_z'][st:st+20]).cuda()
                    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();start=time.monotonic()
                    latent,bb,target=generate(model,decoder,ident,n,st,20,codes,spec['seed'])
                    torch.cuda.synchronize();seconds=time.monotonic()-start;peak=torch.cuda.max_memory_reserved()/2**30
                    if peak>75:raise ValueError('Memory qualification failed')
                    g=out.create_group('new/'+ident);g['latent']=latent;g['backbone']=bb;g['target']=target
                    if row['bucket'] not in seen:
                        seen.add(row['bucket']);outside=torch.from_numpy(fr['train/'+ident+'/reference_z'][:]).cuda()+7
                        other,otherbb,_=generate(model,decoder,ident,n,st,20,codes,spec['seed'],outside=outside)
                        if not np.array_equal(other,latent) or not np.array_equal(otherbb,bb):raise ValueError('Unused scaffold target affected output')
                        g['outside_control_latent']=other;g['outside_control_backbone']=otherbb
                        m['controls'].append(dict(kind='outside',target_id=ident,latent_max_abs=0.,backbone_max_abs=0.))
                    m['batches'].append(dict(target_id=ident,seconds=seconds,peak_reserved_GiB=peak));out.flush();atomic_json(a.output/'manifest.json',m)
                    print('oracle',ident,seconds,flush=True)
        m.update(status='complete',predictions_sha256=sha(a.output/'predictions.h5'))
    except BaseException as error:
        m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-tick;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
