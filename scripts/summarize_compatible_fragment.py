"""Audit frozen compatible inputs, then the unchanged CPU closure on all512outputs."""
import argparse,fcntl,hashlib,json,time
from pathlib import Path
import h5py,numpy as np,torch
from compatible_fragment_core import audit,assemble_inputs
from extra_fragment_validation_core import load_conditions
from local_closure_core import score
from latentfold.local_closure import close_backbone
from latentfold.fragment_conditioning import AMINO_ACIDS
from compare_extra_fragment_refolds import clustered
from prepare_overfit import sha
from profile_gpu import atomic_json


def array_hash(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def expected_controls(ids,control_ids):
    keys={('encoding',i,None) for i in ids}
    for i in control_ids:
        for kind in ('generated','native'):
            keys.update((p+'_'+kind,i,None) for p in ('original','desired','pose_encoding','pose'))
            keys.update(('nonleak',i,mode+'_'+kind+'_compatible') for mode in ('trained','untrained'))
    return keys


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];spec,gc,parent=audit(c)
    if m['status']!='complete':return dict(status='failed',qualified=False,error=m.get('error'),manifest_sha256=sha(mp))
    ids=[r['id'] for r in c['selected']];arms=spec['arms']
    control_ids={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
    wanted=expected_controls(ids,control_ids)
    if (len(m['controls'])!=len(wanted) or {(r['kind'],r['target_id'],r.get('arm')) for r in m['controls']}!=wanted
            or m['training_updates_executed'] or m['initial_weights']!=m['final_weights']
            or m['initial_weights']['trained']!=parent['evaluated_model_sha256']
            or m['initial_weights']['untrained']!=parent['initial_model_sha256']
            or m['initial_weights']['decoder']!=parent['frozen_original']
            or m['peak_reserved_GiB']>75 or m['predictions_sha256']!=sha(run/'predictions.h5')
            or len(m['timing'])!=128 or {(r['arm'],r['target_id']) for r in m['timing']}!={(a,i) for a in arms for i in ids}):
        raise ValueError('Incomplete compatibility diagnostic')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');controls=[];records=[]
    def check(kind,ident,value,expected,threshold,arm=None):
        if value.shape!=expected.shape or not np.isfinite(value).all():raise ValueError('Invalid numerical control array')
        error=float(np.max(np.abs(value-expected)))
        logged=next(r for r in m['controls'] if (r['kind'],r['target_id'],r.get('arm'))==(kind,ident,arm))
        if error>threshold or abs(error-logged['max_abs'])>1e-9:raise ValueError('Numerical control differs: '+kind)
        controls.append(dict(kind=kind,target_id=ident,arm=arm,max_abs=error))
    cache_path=run/'closure_manifest.json';cache_file=run/'closed.h5';source_hash=sha(run/'predictions.h5')
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else dict(status='running',source_predictions_sha256=source_hash,
        closure_protocol_sha256=sha(c['closure_protocol']),closure_code_sha256=sha(c['closure_code']),records={})
    if (cache['source_predictions_sha256']!=source_hash or cache['closure_protocol_sha256']!=sha(c['closure_protocol'])
            or cache['closure_code_sha256']!=sha(c['closure_code'])):raise ValueError('Changed CPU closure cache inputs')
    if cache['status']=='complete' and cache['closed_sha256']!=sha(cache_file):raise ValueError('Changed completed CPU closure cache')
    closure_spec=json.loads(Path(c['closure_protocol']).read_text());deadline=time.monotonic()+1200
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['source_predictions']) as prior, \
         h5py.File(c['noise_source']) as noise_file,h5py.File(cache_file,'a') as closed:
        if (set(f)!=set(arms)|{'noise','controls','inputs'} or any(set(f[a])!=set(ids) for a in arms)
                or set(f['inputs'])!={'generated','native'} or set(f['noise'])!=set(ids)):
            raise ValueError('Changed compatible-output denominator')
        for row in c['selected']:
            ident=row['id'];n=row['length'];original_item=items[ident]
            if not np.array_equal(f['noise/'+ident][:],noise_file['noise/'+ident][:]):raise ValueError('Changed saved decoder noise')
            check('encoding',ident,f['controls/encoding/'+ident][:],original_item['features'][original_item['keep'],:8].numpy(),1e-4)
            for kind,group in (('generated','parent'),('native','native_direct')):
                inputs=f['inputs/'+kind+'/'+ident];reference=prior[group+'/'+ident+'/backbone'][:]
                context=prior[group+'/'+ident+'/latent'][:];sequence=str(inputs.attrs['sequence']);start=int(inputs.attrs['start'])
                expected_sequence=''.join(AMINO_ACIDS[int(x)] for x in original_item['features'][original_item['keep'],8:28].argmax(-1))
                if start!=original_item['start'] or sequence!=expected_sequence or not np.array_equal(inputs['context'][:],context):
                    raise ValueError('Changed context or placement')
                # Rebuild every slot's canonical coordinates, positional/sequence
                # features and placed anchors from its own parent and saved code.
                saved_codes=inputs['isolated_latent'][:];calls=[]
                def saved_encoder(fragment):
                    index=len(calls);calls.append(fragment.numpy());return torch.from_numpy(saved_codes[index:index+1])
                reconstructed=assemble_inputs(torch.from_numpy(reference),sequence,start,saved_encoder)
                for key,value in reconstructed.items():
                    actual=inputs[key][:];expected=value.numpy()
                    tolerance=1e-4 if key=='anchors' else 0
                    if actual.shape!=expected.shape or not np.isfinite(actual).all() or np.max(np.abs(actual.astype(float)-expected.astype(float)))>tolerance:
                        raise ValueError('Mixed slots or changed isolated input: '+key)
                if len(calls)!=4 or saved_codes.shape!=(4,20,8):raise ValueError('Each slot must encode only its own20residue fragment')
                centered=reference-reference.mean((1,2),keepdims=True);keep=inputs['keep'][:].astype(bool)
                if np.max(np.abs(inputs['anchors'][:][keep]-centered[keep]))>1e-4:raise ValueError('Self-compatible anchors differ from parent')
                if ident in control_ids:
                    check('original_'+kind,ident,f['controls/original/'+kind+'/'+ident][:],reference,1e-5)
                    check('desired_'+kind,ident,f['controls/desired/'+kind+'/'+ident][:],prior[kind+'_cond/'+ident+'/backbone'][:],1e-5)
                    check('pose_encoding_'+kind,ident,f['controls/pose_latent/'+kind+'/'+ident][:],saved_codes,1e-4)
                    check('pose_'+kind,ident,f['controls/pose/'+kind+'/'+ident][:],f['trained_'+kind+'_compatible/'+ident+'/backbone'][:],1e-4)
                for mode in ('trained','untrained'):
                    arm=mode+'_'+kind+'_compatible';backbones=f[arm+'/'+ident+'/backbone'][:]
                    if backbones.shape!=(4,n,4,3) or not np.isfinite(backbones).all():raise ValueError('Invalid complete backbone output')
                    if np.max(np.abs(backbones[keep]-inputs['anchors'][:][keep]))>1e-4 or np.max(np.abs(backbones.mean((1,2))))>1e-4:
                        raise ValueError('Fixed anchors or full-chain center drifted')
                    if ident in control_ids:check('nonleak',ident,f['controls/nonleak/'+arm+'/'+ident][:],backbones,1e-5,arm)
                    for slot,bb in enumerate(backbones):
                        key=arm+'/'+ident+'/'+str(slot)
                        item=dict(original_item,id=ident,fragment=inputs['fragment'][slot])
                        raw=score(bb,bb,reference[slot],item,arm,slot,row['bucket'])
                        if key in cache['records']:
                            repaired=closed[key][:]
                            if array_hash(repaired)!=cache['records'][key]['array_sha256']:raise ValueError('Changed cached closure output')
                        else:
                            repaired,stats=close_backbone(bb,reference[slot],start,20,closure_spec,deadline=deadline)
                            if key in closed:del closed[key]
                            closed[key]=repaired;closed.flush()
                            cache['records'][key]=dict(stats,array_sha256=array_hash(repaired));atomic_json(cache_path,cache)
                        after=score(repaired,bb,reference[slot],item,arm,slot,row['bucket'])
                        records.append(dict(arm=arm,target_id=ident,slot=slot,bucket=row['bucket'],raw=raw,closed=after))
        if len(records)!=512 or len(cache['records'])!=512:raise ValueError('Incomplete compatible closure inventory')
    cache.update(status='complete',closed_sha256=sha(cache_file));atomic_json(cache_path,cache)
    summary=[]
    for arm in arms:
        rr=[r for r in records if r['arm']==arm]
        summary.append(dict(arm=arm,samples=len(rr),raw_coarse=sum(r['raw']['coarse_valid'] for r in rr),
            raw_connected=sum(r['raw']['connected_raw'] for r in rr),raw_complete=sum(r['raw']['qualified_raw'] for r in rr),
            closed_coarse=sum(r['closed']['coarse_valid'] for r in rr),closed_connected=sum(r['closed']['connected_raw'] for r in rr),
            closed_complete=sum(r['closed']['qualified_raw'] for r in rr)))
    original=json.loads(Path(c['closure_report']).read_text());old={(r['arm'],r['target_id'],r['generation_slot']):r for r in original['records']}
    contrasts=[]
    for arm,baseline in [('trained_generated_compatible','generated_cond'),('untrained_generated_compatible','generated_untrained'),('trained_native_compatible','native_cond')]:
        rr={(r['target_id'],r['slot']):r for r in records if r['arm']==arm}
        contrasts.append(dict(arm=arm,original_desired_arm=baseline,closed_complete_difference=clustered([
            np.mean([int(rr[i,k]['closed']['qualified_raw'])-int(old[baseline,i,k]['qualified_raw']) for k in range(4)]) for i in ids])))
    totals={r['arm']:r['closed_complete'] for r in summary}
    next_route='global_scaffold_remodeling' if totals['trained_generated_compatible']>=103 else 'generated_context_training_control' if totals['trained_native_compatible']>=103 else 'audit_remaining_geometry'
    return dict(status='complete',diagnostic_only=True,numerically_qualified=True,manifest_sha256=sha(mp),
        predictions_sha256=source_hash,closed_sha256=sha(cache_file),closure_manifest_sha256=sha(cache_path),
        controls=len(controls),summary=summary,contrasts=contrasts,next_route=next_route,records=records,
        gpu_elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],
        cpu_closure_seconds=sum(r['seconds'] for r in cache['records'].values()),
        scope='Artificial compatible-fragment diagnostic,32training proteins andfour original noises. Replacing the desired motif with model-own geometry cannot demonstrate scaffolding or designability. Same frozen decoder/context/noise; only isolated condition changed. Original desired-fragment failures remain closed. No refolding licensed.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    torch.set_num_threads(1);run=a.runs[0]
    with (run/'compatible_audit.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);d=analyze(run)
        a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');visible={k:v for k,v in d.items() if k!='records'}
        a.output.with_suffix('.md').write_text('# Frozen compatible-fragment diagnostic\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n')
        print(json.dumps(visible))


if __name__=='__main__':main()
