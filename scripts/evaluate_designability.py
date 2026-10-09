"""ProteinMPNN plus guarded teacher refolding with no silently dropped outputs."""
import argparse,hashlib,json,subprocess,sys,time
IMPORT_START=time.monotonic()
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.teacher import fast_features,load_fast_model
from latentfold.precision import inference_precision
from latentfold.metrics import usalign_coordinates,ca_metrics
from benchmark_esmfold2 import backbone_indices
from designability_core import design_sequences,write_ca_pdb,write_backbone_pdb
from prepare_overfit import sha
from profile_gpu import Telemetry,atomic_json
from ordered_cpu_scoring import OrderedCPUScoring


def score_refold(record,bb,reference,binary):
    return dict(record,sc_tm=usalign_coordinates(binary,bb[:,1],reference[:,1]),**ca_metrics(bb[:,1],reference[:,1]))


def main():
    import_seconds=time.monotonic()-IMPORT_START
    p=argparse.ArgumentParser()
    for key in ('source','config','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--overlap-cpu-scoring',action='store_true')
    a=p.parse_args();preflight_start=time.monotonic();c=json.loads(a.config.read_text())
    from teacher_numerical_recovery import audit_recovery
    recovered=audit_recovery(c)
    if c.get('teacher_deterministic_algorithms') and c.get('assay') not in ('extra_fragment_refold','fragment_preference_refold'):raise ValueError('Undeclared deterministic teacher assay')
    cpu_verified=c.get('torsion_closure_refold') is True or c.get('retrieved_context_refold') is True
    if cpu_verified:
        if c.get('retrieved_context_refold'):
            from retrieved_context_refolding import audit_worker
        else:
            from torsion_closure_refolding import audit_worker
        audit_worker(c)
    else:
        for key in ('generation_manifest','predictions','protocol','usalign'):
            if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
        for dep in c['dependencies']+c['teacher_artifacts']:
            if sha(dep['path'])!=dep['sha256']:raise ValueError('Changed dependency '+dep['path'])
    expected_count={'generative_pilot':52,'noise_contact':28,'isolated_motif':20,'fixed_motif':20,'trained_fragment':36,'fragment_fixed_positive':4,'fragment_feedback_profile':2,'fragment_feedback':24,'fragment_strict_followup':c.get('expected_backbones',4),'fragment_repetition_refold':c.get('expected_backbones'),'fragment_refinement':6,'fragment_full_backbone':4,'fragment_endpoint_refold':36,'fragment_validation_refold':c.get('expected_backbones'),'extra_fragment_refold':c.get('expected_backbones'),'fragment_source_refold':c.get('expected_backbones'),'fragment_preference_refold':c.get('expected_backbones')}.get(c.get('assay','generative_pilot'))
    if c['num_sequences']!=8 or c['temperature']!=.1 or expected_count is None or len(c['entries'])!=expected_count:raise ValueError('Unexpected design profile')
    if c.get('assay')=='noise_contact':
        from prepare_noise_designability import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='isolated_motif':
        from prepare_fragment_designability import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fixed_motif':
        from prepare_fixed_motif_designability import audit_fixed_inputs
        audit_fixed_inputs(c)
    if c.get('assay')=='trained_fragment':
        from prepare_trained_fragment_designability import audit_inputs
        audit_inputs(c,check_teacher=False)  # Already verified above, before any model use.
    if c.get('assay') in ('fragment_feedback_profile','fragment_feedback'):
        from prepare_fragment_feedback import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fragment_strict_followup':
        from prepare_fragment_strict_followup import audit_inputs
        audit_inputs(c,check_teacher=False)
    if c.get('assay')=='fragment_repetition_refold':
        from prepare_fragment_repetition_refold import audit_inputs
        audit_inputs(c,check_teacher=False)
    if c.get('mpnn_mode','ca') not in ('ca','backbone') or (c.get('mpnn_mode')=='backbone')!=(c.get('assay')=='fragment_full_backbone'):raise ValueError('Undeclared MPNN design mode')
    if c.get('assay')=='fragment_preference_refold' and not cpu_verified:
        from prepare_fragment_preference_refold import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fragment_source_refold':
        from prepare_fragment_source_refold import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='extra_fragment_refold':
        from prepare_extra_fragment_refold import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fragment_validation_refold':
        from prepare_fragment_validation_refold import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fragment_endpoint_refold':
        from prepare_fragment_endpoint_refold import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fragment_full_backbone':
        from prepare_fragment_full_backbone import audit_inputs
        audit_inputs(c)
    if c.get('assay')=='fragment_refinement':
        from fragment_refinement_core import audit_assay
        audit_assay(c)
    if c.get('assay')=='fragment_fixed_positive':
        from prepare_fragment_fixed_positive import audit_inputs
        audit_inputs(c)
    preflight_seconds=time.monotonic()-preflight_start
    a.output.mkdir(parents=True,exist_ok=False);inputs=a.output/'inputs';inputs.mkdir();torch.set_num_threads(4)
    scorer=OrderedCPUScoring(a.overlap_cpu_scoring)
    start=time.monotonic();telemetry=None;m=dict(import_seconds=import_seconds,preflight_seconds=preflight_seconds,cpu_scoring_mode='overlapped' if a.overlap_cpu_scoring else 'serial',status='running',config=c,records=[],controls=[],sequences={},training_updates_executed=0);atomic_json(a.output/'manifest.json',m)
    try:
        torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(.85)
        if recovered is not None or c.get('teacher_deterministic_algorithms'):torch.use_deterministic_algorithms(True)
        m['teacher_deterministic_algorithms']=torch.are_deterministic_algorithms_enabled()
        telemetry=Telemetry(a.output,True);backbones={}
        m['cuda_and_telemetry_seconds']=time.monotonic()-start;export_start=time.monotonic()
        with h5py.File(c['predictions']) as f:
            for r in c['entries']:
                bb=f[r['dataset']][:] if r['head']=='experimental' else f[r['dataset']][r['slot']]
                if bb.shape!=(r['length'],4,3) or not np.isfinite(bb).all():raise ValueError('Invalid input')
                backbones[r['name']]=bb
                if c.get('mpnn_mode')=='backbone':write_backbone_pdb(inputs/(r['name']+'.pdb'),bb)
                else:write_ca_pdb(inputs/(r['name']+'.pdb'),bb[:,1])
        m['backbone_export_seconds']=time.monotonic()-export_start
        mpnn=Path(c['mpnn']);parsed=a.output/'parsed.jsonl';designs=a.output/'mpnn';tick=time.monotonic()
        mode_args=[] if c.get('mpnn_mode')=='backbone' else ['--ca_only']
        model_weights='vanilla_model_weights' if c.get('mpnn_mode')=='backbone' else 'ca_model_weights'
        from fixed_motif_design import requires_fixed_motifs,verify_fixed_sequences
        constrained=requires_fixed_motifs(c['entries'])
        with (a.output/'mpnn.log').open('w') as log:
            subprocess.run([sys.executable,str(mpnn/'helper_scripts/parse_multiple_chains.py'),'--input_path',str(inputs),'--output_path',str(parsed)]+mode_args,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
            m['mpnn_parse_seconds']=time.monotonic()-tick
            fixed_args=[]
            if constrained:
                from fixed_motif_design import fix_parsed_motifs
                positions=a.output/'fixed_positions.jsonl';fix_parsed_motifs(parsed,positions,c['entries']);fixed_args=['--fixed_positions_jsonl',str(positions)]
            subprocess.run([sys.executable,str(mpnn/'protein_mpnn_run.py'),'--jsonl_path',str(parsed),'--out_folder',str(designs),*mode_args,'--path_to_model_weights',str(mpnn/model_weights),'--model_name','v_48_020','--num_seq_per_target','8','--sampling_temp','0.1','--seed','1','--batch_size','1']+fixed_args,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        m['mpnn_seconds']=time.monotonic()-tick
        for r in c['entries']:m['sequences'][r['name']]=design_sequences(designs/'seqs'/(r['name']+'.fa'),r['length'])
        verify_fixed_sequences(m['sequences'],c['entries'])
        if recovered is not None and m['sequences']!=recovered['sequences']:raise ValueError('Recovery changed fixed sequence attempts')
        if len(list((designs/'seqs').glob('*.fa')))!=len(c['entries']):raise ValueError('Unexpected design coverage')
        atomic_json(a.output/'manifest.json',m);print('MPNN complete',len(c['entries']),flush=True)
        load_start=time.monotonic()
        model,m['teacher_adapter']=load_fast_model(a.source/'data/esmfold2_fast')
        m['teacher_load_seconds']=time.monotonic()-load_start;atomic_json(a.output/'manifest.json',m)
        with torch.no_grad(),inference_precision('fp32'),h5py.File(a.output/'refolded.h5','x') as f:
            for r in c['entries']:
                name=r['name'];ref=backbones[name];g=f.create_group(name)
                for index,seq in enumerate(m['sequences'][name]):
                    if time.monotonic()-start>c['work_cap_seconds']:raise TimeoutError('Designability cap')
                    seed=int.from_bytes(hashlib.sha256(f"{c['seed']}:{name}:{index}".encode()).digest()[:8],'little')%(2**63-1);torch.manual_seed(seed);torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();tick=time.monotonic()
                    features=fast_features(seq);indices=backbone_indices(features,len(seq));output=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1);bb=output.sample_atom_coords.float().cpu().numpy()[0,indices,:];del output;torch.cuda.synchronize();seconds=time.monotonic()-tick
                    if bb.shape!=ref.shape or not np.isfinite(bb).all():raise ValueError('Invalid refold, retain failure in manifest')
                    if recovered is not None and name==recovered['records'][0]['name'] and index==0:
                        with h5py.File(c['numerical_recovery']['failed_refolded']) as old_file:previous=old_file[name+'/0'][:]
                        m['recovery_control']=ca_metrics(previous[:,1],bb[:,1]);atomic_json(a.output/'manifest.json',m)
                        if m['recovery_control']['ca_rmsd']>.01 or m['recovery_control']['ca_lddt']<.999:raise ValueError('Recovery original-output parity failed')
                    g.create_dataset(str(index),data=bb)
                    record=dict(name=name,sequence_index=index,seed=seed,seconds=seconds,peak_reserved_bytes=torch.cuda.max_memory_reserved())
                    m['records'].extend(scorer.submit(score_refold,record,bb,ref,c['usalign']))
                    if (r['head']=='experimental' or r.get('repeatability_control',False)) and index==0:
                        torch.manual_seed(seed);repeat=model.fold(**features,num_loops=3,num_sampling_steps=50,num_diffusion_samples=1);again=repeat.sample_atom_coords.float().cpu().numpy()[0,indices,:];del repeat;control=dict(name=name,**ca_metrics(bb[:,1],again[:,1]));m['controls'].append(control);atomic_json(a.output/'manifest.json',m)
                        if control['ca_rmsd']>.01 or control['ca_lddt']<.999:raise ValueError('Teacher repeatability failed')
                    f.flush();atomic_json(a.output/'manifest.json',m)
                m['records'].extend(scorer.drain(wait=True));atomic_json(a.output/'manifest.json',m)
                print('refolded',name,'best',max(x['sc_tm'] for x in m['records'] if x['name']==name),flush=True)
        if cpu_verified:
            final_check_start=time.monotonic()
            audit_worker(c)
            m['final_input_identity_check_seconds']=time.monotonic()-final_check_start
            m['cpu_preflight_file_identity_unchanged']=True
        m['status']='complete'
    except BaseException as error:m.update(status='failed',error=f'{type(error).__name__}: {error}');raise
    finally:
        scorer.close();m['cpu_scoring_wait_seconds']=scorer.wait_seconds
        if telemetry:telemetry.close()
        m['elapsed_seconds']=time.monotonic()-start;atomic_json(a.output/'manifest.json',m)

if __name__=='__main__':main()
