"""Matched native-only residual conditioning; inherited generative head frozen."""
import argparse,copy,hashlib,json,math,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.conditioning import ResidualConditioner
from latentfold.decoder import load_proteinae
from latentfold.flow import FlowConfig,SampleConfig,flow_loss,sample,target_noise
from latentfold.precision import inference_precision
from latentfold.metrics import ca_metrics
from profile_gpu import Telemetry,atomic_json
from predict import file_identity


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','config','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text());selection_path=Path(c['selection'])
    if hashlib.sha256(selection_path.read_bytes()).hexdigest()!=c['selection_sha256']:raise ValueError('changed training selection')
    selection=json.loads(selection_path.read_text());a.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic()
    m=dict(status='running',config=c,updates=0,training=[],batches=[],scores=[],controls=[],scope='Native-only conditioning screen. Frozen inherited flow/decoder; only bounded residual adapter learned. No teacher training or confirmation-set scoring.');telemetry=None;atomic_json(a.output/'manifest.json',m)
    try:
        records={};buckets={k:[] for k in (128,256,384,512)}
        with h5py.File(c['embedding_cache']) as cache,h5py.File(selection['dataset']) as source:
            for split in ('train','tuning'):
                if set(cache[split])!={r['id'] for r in selection[split]}:raise ValueError('embedding cache coverage mismatch')
                for r in selection[split]:
                    g=cache[split][r['id']]
                    if g.attrs['sequence_sha256']!=r['sequence_sha256']:raise ValueError('embedding sequence mismatch')
                    original=source['train'][r['id']];records[r['id']]=dict(**r,layers={k:torch.from_numpy(g[str(k)][:]) for k in (20,40,60,80)},z=torch.from_numpy(original['z'][:]),ca=original['ca_coords'][:])
                    if split=='train':buckets[r['bucket']].append(r['id'])
        ckpt=a.source/'data/phase1_dataset/last_pf_459M_p128x8_long512_scratch.ckpt';m['checkpoint']=file_identity(ckpt,hash_contents=True)
        model,_=load_legacy(ckpt,trusted_pickle=True);model.cuda().eval().requires_grad_(False);model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda()
        torch.manual_seed(c['seed']);adapter=ResidualConditioner(c['arm'],width=c['width'],bound=c['bound']).cuda();ema=copy.deepcopy(adapter).eval().requires_grad_(False)
        optimizer=torch.optim.AdamW(adapter.parameters(),lr=c['learning_rate'],betas=(.9,.999),weight_decay=.01,foreach=False)
        m['trainable_parameters']=sum(p.numel() for p in adapter.parameters());order=np.random.default_rng(c['seed']);rng=torch.Generator(device='cuda').manual_seed(c['seed']);queues={k:[] for k in buckets};telemetry=Telemetry(a.output,True)
        def batch(ids,length):
            mask=torch.arange(length,device='cuda')[None]<torch.tensor([records[k]['length'] for k in ids],device='cuda')[:,None]
            layers={k:torch.zeros(len(ids),length,2560,device='cuda') for k in (20,40,60,80)};z=torch.zeros(len(ids),length,8,device='cuda')
            for i,ident in enumerate(ids):
                r=records[ident];n=r['length'];z[i,:n]=r['z'].cuda()
                for layer in layers:layers[layer][i,:n]=r['layers'][layer].cuda()
            return layers,mask,z
        with torch.no_grad():
            for length in buckets:
                layers,mask,_=batch(buckets[length][:2],length);same=torch.equal(adapter(layers,mask),layers[80]);m['controls'].append(dict(length=length,initial_conditioner_exact=same))
                if not same:raise ValueError('adapter changes initial model conditioning')
        def evaluate(step):
            with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/f'evaluation_{step}.h5','x') as out:
                for length in buckets:
                    ids=[r['id'] for r in selection['tuning'] if r['bucket']==length]
                    for offset in range(0,len(ids),8):
                        chunk=ids[offset:offset+8];layers,mask,_=batch(chunk,length);esm=ema(layers,mask);expanded=esm.repeat_interleave(3,0);masks=mask.repeat_interleave(3,0);noise=torch.zeros(len(chunk)*3,length,8,device='cuda');dn=torch.zeros(len(chunk)*3,4*length,3,device='cuda')
                        for i,ident in enumerate(chunk):
                            n=records[ident]['length']
                            for k in range(3):
                                noise[3*i+k,:n]=target_noise([ident],[n],8,seed=c['evaluation_seed'],sample_index=k,device='cuda')[0]
                                dn[3*i+k,:4*n]=target_noise([ident],[4*n],3,seed=c['evaluation_seed'],sample_index=k,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                        z=sample(model,expanded,masks,SampleConfig(steps=25,guidance=2),noise=noise,conditioning_ids=[ident for ident in chunk for _ in range(3)])
                        _,bb=decoder(z,masks,noise=dn,return_backbone=True);bb=bb.cpu().numpy()
                        if step==0 and offset==0:
                            n=records[chunk[0]]['length'];single=sample(model,esm[:1,:n],mask[:1,:n],SampleConfig(steps=25,guidance=2),noise=noise[:1,:n]);alone=decoder(single,mask[:1,:n],noise=dn[:1,:4*n])[0].cpu().numpy();control=ca_metrics(bb[0,:n,1],alone);m['controls'].append(dict(length=length,**control))
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99:raise ValueError('evaluation batching control failed')
                        for i,ident in enumerate(chunk):
                            r=records[ident];pred=bb[3*i:3*i+3,:r['length']];out.create_dataset(ident,data=pred)
                            for k,x in enumerate(pred):m['scores'].append(dict(step=step,target_id=ident,sample=k,**ca_metrics(x[:,1],r['ca'])))
            atomic_json(a.output/'manifest.json',m);print('evaluated',step,flush=True)
        evaluate(0)
        with inference_precision('fp32'):
            for begin,end in ((0,250),(250,500)):
                name=f'collect::conditioning_train::{begin}::{end}';torch.cuda.synchronize();tick=time.monotonic();torch.cuda.reset_peak_memory_stats();torch.cuda.nvtx.range_push(name)
                try:
                    for step in range(begin,end):
                        if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('conditioning experiment work cap')
                        length=sorted(buckets)[step%4];count=c['batches'][str(length)]
                        if len(queues[length])<count:queues[length]=order.permutation(buckets[length]).tolist()
                        ids=queues[length][:count];del queues[length][:count];layers,mask,z=batch(ids,length)
                        progress=step/499;lr=c['learning_rate']*min((step+1)/50,1)*(.1+.9*.5*(1+math.cos(math.pi*progress)));optimizer.param_groups[0]['lr']=lr;optimizer.zero_grad(set_to_none=True)
                        esm,residual=adapter(layers,mask,return_residual=True);flow,_=flow_loss(model,z,esm,mask,FlowConfig(),generator=rng)
                        penalty=(residual.square().mean(-1)*mask).sum()/mask.sum();loss=flow+c['residual_penalty']*penalty
                        if not torch.isfinite(loss):raise FloatingPointError('nonfinite training loss')
                        loss.backward();norm=torch.nn.utils.clip_grad_norm_(adapter.parameters(),1.,error_if_nonfinite=True)
                        if norm<=0:raise FloatingPointError('conditioning gradient vanished')
                        optimizer.step()
                        with torch.no_grad():
                            for ep,ap in zip(ema.parameters(),adapter.parameters()):ep.lerp_(ap,.01)
                        m['updates']=step+1
                        if step%25==0 or step+1==end:
                            m['training'].append(dict(step=step+1,length=length,batch=count,flow_loss=float(flow.detach()),residual_mse=float(penalty.detach()),gradient_norm=float(norm),learning_rate=lr,ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest()));atomic_json(a.output/'manifest.json',m)
                        del layers,mask,z,esm,residual,flow,penalty,loss
                    torch.cuda.synchronize();seconds=time.monotonic()-tick
                finally:torch.cuda.nvtx.range_pop()
                m['batches'].append(dict(nvtx_range=name,seconds=seconds,updates=end-begin,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                torch.save(ema.state_dict(),a.output/f'adapter_{end}.pt');evaluate(end)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
