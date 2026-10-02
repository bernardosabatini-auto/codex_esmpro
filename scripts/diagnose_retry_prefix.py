"""Separate online-embedding and batch-prefix effects without relaxing output controls."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.embedding import FinalESMC
from latentfold.flow import SampleConfig,sample,target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json
from retry_latency_core import bounded_outputs


def compare_outputs(actual,expected,indices,expected_indices):
    if actual.shape!=expected.shape or len(indices)!=len(actual) or len(expected_indices)!=len(actual):raise ValueError('Mismatched comparison scope')
    a=backbone_geometry(actual)['coarse_valid'];b=backbone_geometry(expected)['coarse_valid']
    return [dict(slot=k,selected_draw=int(indices[k]),reference_draw=int(expected_indices[k]),validity_identical=bool(a[k]==b[k]),**ca_metrics(x[:,1],y[:,1])) for k,(x,y) in enumerate(zip(actual,expected))]


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','failed_manifest','ensemble_manifest','reference','panel','checkpoint','embedding_cache','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    old=json.loads(Path(c['ensemble_manifest']).read_text());settings=old['config']
    if old['status']!='complete' or any(c[k]!=settings[k] for k in ('checkpoint_sha256','seed','primary_guidance','flow_steps','compact_condition','panel_sha256','embedding_cache_sha256','decoder_checkpoint_sha256')):raise ValueError('Unmatched original settings')
    panel={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']};rows=[panel[i] for i in c['target_ids']]
    if len(rows)!=8 or len({r['family'] for r in rows})!=8:raise ValueError('Wrong timing diagnostic panel')
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None;m=dict(status='running',config=c,embeddings=[],comparisons=[],predictions=[],training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        telemetry=Telemetry(a.output,True);embedding=FinalESMC(a.source/'data/esmc6b',precision='fp32');model,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);model.cuda().eval().requires_grad_(False);decoder=load_proteinae(a.source/'ProteinAE_v1',Path(c['decoder_checkpoint']),steps=3).cuda().eval();cfg=SampleConfig(steps=c['flow_steps'],guidance=c['primary_guidance'])
        with torch.no_grad(),inference_precision('fp32'),h5py.File(c['embedding_cache']) as cache,h5py.File(c['reference']) as reference,h5py.File(a.output/'predictions.h5','x') as out:
            for row in rows:
                if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Diagnostic cap')
                ident=row['query_id'];n=row['length'];length=next(x for x in (128,256,384,512) if n<=x);mask=torch.arange(length,device='cuda')[None]<n
                cached=torch.zeros(1,length,2560,device='cuda');cached[0,:n]=torch.from_numpy(cache[ident]['80'][:]).cuda();online=embedding([row['sequence']],length);delta=(online-cached)[mask];m['embeddings'].append(dict(target_id=ident,rmse=float(delta.square().mean().sqrt()),max_abs=float(delta.abs().max())))
                dn=torch.zeros(1,4*length,3,device='cuda');dn[0,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=0,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
                g=reference[ident][f"cfg{c['primary_guidance']}/latent"];expected=g['backbone'][:];expected_indices=g['seed_indices'][:,0];outputs={}
                for variant,esm in [('cached',cached),('online',online)]:
                    for count in (1,8,32):
                        def draw(addresses):
                            b=len(addresses);noise=torch.zeros(b,length,8,device='cuda')
                            for j,k in enumerate(addresses):noise[j,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=k,device='cuda')[0]
                            z=sample(model,esm.repeat(b,1,1),mask.repeat(b,1),cfg,noise=noise,conditioning_ids=[ident]*b,compact_condition=c['compact_condition']);_,bb=decoder(z,mask.repeat(b,1),noise=dn.repeat(b,1,1),return_backbone=True);return bb[:,:n].cpu().numpy()
                        bb,info=bounded_outputs(draw,count);outputs[(variant,count)]=(bb,info['selected_draws']);g=out.create_group(f'{ident}/{variant}/{count}');g.create_dataset('backbone',data=bb);g.create_dataset('selected_draws',data=info['selected_draws']);m['predictions'].append(dict(target_id=ident,variant=variant,count=count,**info))
                        m['comparisons'].append(dict(target_id=ident,kind=variant+'_vs_reference',count=count,checks=compare_outputs(bb,expected[:count],info['selected_draws'],expected_indices[:count])))
                for count in (1,8,32):
                    bb,ix=outputs[('online',count)];ref,ri=outputs[('cached',count)];m['comparisons'].append(dict(target_id=ident,kind='online_vs_cached',count=count,checks=compare_outputs(bb,ref,ix,ri)))
                for variant in ('cached','online'):
                    ref,ri=outputs[(variant,32)]
                    for count in (1,8):
                        bb,ix=outputs[(variant,count)];m['comparisons'].append(dict(target_id=ident,kind=variant+'_prefix_vs32',count=count,checks=compare_outputs(bb,ref[:count],ix,ri[:count])))
                out.flush();atomic_json(a.output/'manifest.json',m);print('diagnosed',ident,flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
