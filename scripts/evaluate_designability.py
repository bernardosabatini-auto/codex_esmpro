"""ProteinMPNN plus guarded teacher refolding with no silently dropped outputs."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher import fast_features,load_fast_model
from latentfold.precision import inference_precision
from latentfold.metrics import usalign_coordinates,ca_metrics
from benchmark_esmfold2 import backbone_indices
from designability_core import design_sequences,write_ca_pdb
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json


def main():
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();c=json.loads(a.config.read_text())
    for key in ('generation_manifest','predictions','protocol','usalign'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    for dep in c['dependencies']+c['teacher_artifacts']:
        if sha(dep['path'])!=dep['sha256']:raise ValueError('Changed dependency '+dep['path'])
    expected_count={'generative_pilot':52,'noise_contact':28}.get(c.get('assay','generative_pilot'))
    if c['num_sequences']!=8 or c['temperature']!=.1 or expected_count is None or len(c['entries'])!=expected_count:raise ValueError('Unexpected design profile')
    if c.get('assay')=='noise_contact':
        from prepare_noise_designability import audit_inputs
        audit_inputs(c)
    a.output.mkdir(parents=True,exist_ok=False);inputs=a.output/'inputs';inputs.mkdir();torch.set_num_threads(4)
    start=time.monotonic();telemetry=None;m=dict(status='running',config=c,records=[],controls=[],sequences={},training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        telemetry=Telemetry(a.output,True);backbones={}
        with h5py.File(c['predictions']) as f:
            for r in c['entries']:
                bb=f[r['dataset']][:] if r['head']=='experimental' else f[r['dataset']][r['slot']]
                if bb.shape!=(r['length'],4,3) or not np.isfinite(bb).all():raise ValueError('Invalid input')
                backbones[r['name']]=bb;write_ca_pdb(inputs/(r['name']+'.pdb'),bb[:,1])
        mpnn=Path(c['mpnn']);parsed=a.output/'parsed.jsonl';designs=a.output/'mpnn';tick=time.monotonic()
        with (a.output/'mpnn.log').open('w') as log:
            subprocess.run([sys.executable,str(mpnn/'helper_scripts/parse_multiple_chains.py'),'--input_path',str(inputs),'--output_path',str(parsed),'--ca_only'],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
            subprocess.run([sys.executable,str(mpnn/'protein_mpnn_run.py'),'--jsonl_path',str(parsed),'--out_folder',str(designs),'--ca_only','--path_to_model_weights',str(mpnn/'ca_model_weights'),'--model_name','v_48_020','--num_seq_per_target','8','--sampling_temp','0.1','--seed','1','--batch_size','1'],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        m['mpnn_seconds']=time.monotonic()-tick
        for r in c['entries']:m['sequences'][r['name']]=design_sequences(designs/'seqs'/(r['name']+'.fa'),r['length'])
        if len(list((designs/'seqs').glob('*.fa')))!=len(c['entries']):raise ValueError('Unexpected design coverage')
        atomic_json(a.output/'manifest.json',m);print('MPNN complete',len(c['entries']),flush=True)
        model,m['teacher_adapter']=load_fast_model(a.source/'data/esmfold2_fast');atomic_json(a.output/'manifest.json',m)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'refolded.h5','x') as f:
            for r in c['entries']:
                name=r['name'];ref=backbones[name];g=f.create_group(name)
                for index,seq in enumerate(m['sequences'][name]):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Designability cap')
                    seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{name}:{index}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed);torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                    features=fast_features(seq);indices=backbone_indices(features,len(seq));output=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1);bb=output.sample_atom_coords.float().cpu().numpy()[0,indices,:];del output;torch.cuda.synchronize();seconds=time.monotonic()-tick
                    if bb.shape!=ref.shape or not np.isfinite(bb).all():raise ValueError('Invalid refold, retain failure in manifest')
                    g.create_dataset(str(index),data=bb);metric=usalign_coordinates(c['usalign'],bb[:,1],ref[:,1]);m['records'].append(dict(name=name,sequence_index=index,seed=seed,sc_tm=metric,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved(),**ca_metrics(bb[:,1],ref[:,1])))
                    if r['head']=='experimental' and index==0:
                        torch.manual_seed(seed);repeat=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1);again=repeat.sample_atom_coords.float().cpu().numpy()[0,indices,:];del repeat;control=dict(name=name,**ca_metrics(bb[:,1],again[:,1]));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                        if control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Teacher repeatability failed')
                    f.flush();atomic_json(a.output/'manifest.json',m)
                print('refolded',name,'best',max(x['sc_tm'] for x in m['records'] if x['name']==name),flush=True)
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
