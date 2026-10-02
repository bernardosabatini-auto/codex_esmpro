"""Same-device graph replay controls and cached-embedding generation timing."""
import argparse,gc,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from cuda_graph_sample import CapturedFlow
from latentfold.checkpoints import load_legacy
from latentfold.decoder import load_proteinae
from latentfold.flow import sample,SampleConfig,target_noise
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.precision import inference_precision
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('protocol','panel','checkpoint','embedding_cache','quality_report','source_latency_config'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    if not json.loads(Path(c['quality_report']).read_text())['sampling_quality_gate_passed']:raise ValueError('source model not qualified')
    protocol=json.loads(Path(c['protocol']).read_text());rows={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']};rows={i:rows[i] for i in c['target_ids']}
    if len(rows)!=8 or len({r['family'] for r in rows.values()})!=8:raise ValueError('eight development families required')
    records={}
    with h5py.File(c['embedding_cache']) as h:
        for ident,r in rows.items():
            if h[ident].attrs['sequence_sha256']!=hashlib.sha256(r['sequence'].encode()).hexdigest():raise ValueError('sequence identity changed')
            records[ident]=h[ident]['80'][:]
    a.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4);torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85);start=time.monotonic();telemetry=None
    m=dict(status='running',config=c,controls=[],rows=[],construction=[],batches=[]);atomic_json(a.output/'manifest.json',m)
    try:
        m['gpu']=torch.cuda.get_device_name(0)
        if 'RTX PRO 6000' not in m['gpu']:raise ValueError('RTX hardware required')
        net,_=load_legacy(Path(c['checkpoint']),trusted_pickle=True);net.cuda().eval().requires_grad_(False)
        decoder=load_proteinae(a.source/'ProteinAE_v1',a.source/'ProteinAE_v1/checkpoints/ae_r1_d8_v1.ckpt',steps=3).cuda();telemetry=Telemetry(a.output,True)
        def inputs(ident,length,count,repeat):
            n=rows[ident]['length'];esm=torch.zeros(1,length,2560,device='cuda');esm[0,:n]=torch.from_numpy(records[ident]).cuda();mask=torch.arange(length,device='cuda')[None]<n;noise=torch.zeros(count,length,8,device='cuda');dn=torch.zeros(count,4*length,3,device='cuda')
            for k in range(count):
                noise[k,:n]=target_noise([ident],[n],8,seed=c['seed'],sample_index=repeat*32+k,device='cuda')[0]
                dn[k,:4*n]=target_noise([ident],[4*n],3,seed=c['seed'],sample_index=repeat,stream='decoder',device='cuda')[0]*decoder.fm.scale_ref
            return esm,mask,noise,dn
        with torch.no_grad(),inference_precision('fp32'):
            for length in (128,256,384,512):
                ids=[i for i,r in rows.items() if next(b for b in (128,256,384,512) if r['length']<=b)==length]
                if not ids:continue
                for count in (1,32):
                    esm,mask,noise,dn=inputs(ids[0],length,count,0);torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();captured=CapturedFlow(net,esm,mask,noise);construction_seconds=time.monotonic()-tick
                    m['construction'].append(dict(length=length,samples=count,seconds=construction_seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                    if torch.cuda.max_memory_reserved()>80*1024**3:raise MemoryError('graph construction exceeds80GiB')
                    # Warm both complete cached-input pipelines before timed repeats.
                    for kind in ('eager','captured'):
                        z=captured(esm,mask,noise) if kind=='captured' else sample(net,esm.repeat(count,1,1),mask.repeat(count,1),SampleConfig(25,1),noise=noise,conditioning_ids=[ids[0]]*count,compact_condition=True)
                        _,bb=decoder(z,mask.repeat(count,1),noise=dn,return_backbone=True);del z,bb
                    torch.cuda.synchronize()
                    for ident in ids:
                        n=rows[ident]['length']
                        for repeat in range(3):
                            if time.monotonic()-start>840:raise TimeoutError('graph profile work cap')
                            esm,mask,noise,dn=inputs(ident,length,count,repeat);outputs={}
                            for kind in (('eager','captured') if repeat%2==0 else ('captured','eager')):
                                name=f'collect::graph::{ident}::{count}::{repeat}::{kind}';torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic();torch.cuda.nvtx.range_push(name)
                                try:
                                    z=captured(esm,mask,noise) if kind=='captured' else sample(net,esm.repeat(count,1,1),mask.repeat(count,1),SampleConfig(25,1),noise=noise,conditioning_ids=[ident]*count,compact_condition=True)
                                    _,bb=decoder(z,mask.repeat(count,1),noise=dn,return_backbone=True);backbone=bb[:,:n].cpu().numpy();torch.cuda.synchronize();seconds=time.monotonic()-tick
                                finally:torch.cuda.nvtx.range_pop()
                                outputs[kind]=(z.cpu().numpy(),backbone);m['rows'].append(dict(target_id=ident,family=rows[ident]['family'],samples=count,repeat=repeat,kind=kind,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved()));m['batches'].append(dict(nvtx_range=name));del z,bb
                            dz=outputs['captured'][0]-outputs['eager'][0];scores=[ca_metrics(a[:,1],b[:,1]) for a,b in zip(outputs['captured'][1],outputs['eager'][1])]
                            valid=[backbone_geometry(outputs[k][1])['coarse_valid'] for k in ('eager','captured')]
                            control=dict(target_id=ident,samples=count,repeat=repeat,latent_rmse=float(np.sqrt(np.mean(dz**2))),latent_max_abs=float(np.abs(dz).max()),max_ca_rmsd=max(r['ca_rmsd'] for r in scores),min_ca_lddt=min(r['ca_lddt'] for r in scores),validity_exact=bool(np.array_equal(*valid)))
                            tol=protocol['controls'];control['passed']=bool(control['latent_rmse']<=tol['max_latent_rmse'] and control['latent_max_abs']<=tol['max_latent_abs'] and control['max_ca_rmsd']<=tol['max_ca_rmsd'] and control['min_ca_lddt']>=tol['min_ca_lddt'] and control['validity_exact']);m['controls'].append(control)
                            if not control['passed']:raise ValueError('graph output agreement failed')
                            atomic_json(a.output/'manifest.json',m)
                        print(ident,count,'controlled',flush=True)
                    del captured,esm,mask,noise,dn,outputs;gc.collect();torch.cuda.empty_cache()
        if len(m['controls'])!=48 or len(m['rows'])!=96:raise ValueError('incomplete timing/control panel')
        m['qualified']=max(r['peak_reserved_bytes'] for r in m['rows']+m['construction'])<=80*1024**3;m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)


if __name__=='__main__':main()
