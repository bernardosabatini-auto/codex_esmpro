"""Audit saved whole-chain clock weights and all generated/native/initial-path outputs."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.masked_fragment_flow import editable_window
from latentfold.unconditional_training import UNUSED_PREFIXES
from latentfold.flow import target_noise
from latentfold.metrics import ca_metrics
from masked_fragment_training_core import load_training,training_batch,panel
from scaffold_clock_training_core import audit,initial_state,quality_gate
from extra_fragment_validation_core import load_conditions
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from native_anchor_training_core import state_hash,tensor_hash
from prepare_overfit import sha
from compare_extra_fragment_refolds import clustered


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text()) if mp.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];spec=audit(c);selected=panel(c);ids=[r['id'] for r in selected];data=load_training(c)
    if (m['updates']!=c['updates'] or len(m['training'])!=c['updates'] or m['peak_reserved_GiB']>75
        or m['initial_codec_sha256']!=m['final_codec_sha256'] or m['initial_model_sha256']==m['final_model_sha256']
        or m['checkpoint_sha256']!=sha(run/'checkpoint.pt') or m['predictions_sha256']!=sha(run/'predictions.h5')
        or len(m['controls'])!=4*len(ids) or len(m['evaluations'])!=4*len(ids)):raise ValueError('Changed training inventory/checkpoint/frozen state')
    ck=torch.load(run/'checkpoint.pt',map_location='cpu',weights_only=True,mmap=True)
    if ck['config']!=c or state_hash(ck['raw'])!=m['final_model_sha256'] or any(not torch.isfinite(v).all() for mode in ('raw','ema') for v in ck[mode].values()):raise ValueError('Invalid saved model')
    initial=initial_state(c)
    if state_hash(initial)!=m['initial_model_sha256'] or set(initial)!=set(ck['raw']) or set(initial)!=set(ck['ema']):raise ValueError('Changed pretrained initialization or state inventory')
    frozen=sorted(k for k in initial if k.startswith(tuple('net.'+p for p in UNUSED_PREFIXES)))
    if sorted(m['frozen_names'])!=frozen or m['frozen_initial']!=m['frozen_final'] or m['frozen_initial']!=state_hash({k:initial[k] for k in frozen}):raise ValueError('Changed unused frozen parameters')
    if any(not torch.equal(ck[mode][k],initial[k]) for mode in ('raw','ema') for k in frozen):raise ValueError('Saved raw/EMA frozen state changed')
    del initial
    order=np.random.default_rng(spec['seed']);buckets={b:sorted(i for i,r in data.items() if r['bucket']==b) for b in (128,256,384,512)}
    for step,r in enumerate(m['training']):
        length=(128,256,384,512)[step%4];batch=spec['batches'][str(length)];draws=order.choice(buckets[length],size=batch).tolist();names=order.choice(spec['conditions'],size=batch).tolist()
        factor=min((step+1)/spec['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*step/(spec['updates']-1))))
        if (r['step']!=step+1 or r['length']!=length or r['batch']!=batch or r['ids']!=draws or r['conditions']!=names or r['learning_rate_factor']!=factor
            or not math.isfinite(r['loss']) or not math.isfinite(r['gradient_norm']) or r['gradient_norm']<=0 or r['target_sha256']!=tensor_hash(training_batch(data,draws,names,length)[0])):raise ValueError('Changed training draw/target/schedule')
    prefix_error=None
    if not c['profile_only']:
        pm=json.loads(Path(c['profile_manifest']).read_text());keys=('step','length','batch','ids','conditions','learning_rate_factor','target_sha256','noise_sha256','time_sha256','drop_sha256','self_conditioned','clock_sha256','de_novo_sha256')
        if pm['initial_model_sha256']!=m['initial_model_sha256'] or len(pm['training'])!=40 or any(x[k]!=y[k] for x,y in zip(pm['training'],m['training'][:40]) for k in keys) or m['prefix_sha256']!=sha(run/'prefix_40.pt'):raise ValueError('Unmatched profile/full prefix')
        pck=torch.load(c['profile_checkpoint'],map_location='cpu',weights_only=True,mmap=True);prefix=torch.load(run/'prefix_40.pt',map_location='cpu',weights_only=True,mmap=True)
        prefix_error=max(float((prefix[mode][k]-pck[mode][k]).abs().max()) for mode in ('raw','ema') for k in prefix[mode])
        if prefix_error>1e-4:raise ValueError('Profile/full numerical prefix failed')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');records=[];replay=[]
    arms=('parent','native_direct','generated_cond','generated_null','native_cond','native_null')
    expected_controls={(i,k) for i in ids for k in ('parent','native_direct','generated_cond_pose','native_cond_pose')}
    if {(r['target_id'],r['kind']) for r in m['controls']}!=expected_controls:raise ValueError('Incomplete control inventory')
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['baseline_predictions']) as old,h5py.File(c['diagnostic_predictions']) as original_native:
        if set(f)!=set(arms) or any(set(f[k])!=set(ids) for k in f):raise ValueError('Changed evaluation inventory')
        for source in selected:
            ident=source['id'];item=items[ident];n=item['length'];keep=item['keep'][None].expand(4,-1);mask=torch.ones(4,n,dtype=torch.bool);edit=editable_window(keep,mask,spec['flank']).numpy()
            for arm in ('parent','native_direct'):
                g=f[arm+'/'+ident];context=old['new/'+ident+'/latent'][:] if arm=='parent' else np.repeat(data[ident]['target'].numpy()[None],4,axis=0)
                reference=old['new/'+ident+'/backbone'][:] if arm=='parent' else original_native['native/'+ident+'/backbone'][:4]
                if not np.array_equal(g['latent'][:],context):raise ValueError('Changed source context')
                check=check_backbones(g['backbone'][:],reference,item['fragment'],item['start'],ident);logged=next(r for r in m['controls'] if r['target_id']==ident and r['kind']==arm)
                if any(check[k]!=logged[k] for k in check):raise ValueError('Changed historical/native parity')
            for arm in arms:
                g=f[arm+'/'+ident];z=g['latent'][:];bb=g['backbone'][:]
                if z.shape!=(4,n,8) or bb.shape!=(4,n,4,3) or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Invalid saved evaluation')
                context_arm='native_direct' if arm.startswith('native') else 'parent';context=f[context_arm+'/'+ident+'/latent'][:];base=f[context_arm+'/'+ident+'/backbone'][:]
                if arm.endswith('_cond'):
                    error=float(np.max(abs(g['pose_latent'][:]-z)));logged=next(r for r in m['controls'] if r['target_id']==ident and r['kind']==arm+'_pose')
                    if not np.isfinite(error) or error>1e-4 or error!=logged['latent_max_abs']:raise ValueError('Changed supplied-coordinate pose result')
                rr=raw_rows(bb,item['fragment'],item['start'],arm,ident,item['family'])
                for k,r in enumerate(rr):
                    scores=ca_metrics(bb[k,~edit[k],1],base[k,~edit[k],1]);records.append(dict(r,bucket=source['bucket'],scaffold_ca_rmsd=scores['ca_rmsd'],scaffold_ca_lddt=scores['ca_lddt']))
                if ident==ids[0] and arm in ('generated_cond','native_cond'):
                    predicted=g['reloaded_latent'][:];error=float(np.max(abs(predicted-z)))
                    logged=next(r for r in m['checkpoint_replay'] if (r['arm'],r['target_id'])==(arm,ident))
                    if predicted.shape!=z.shape or not np.isfinite(predicted).all() or error>1e-5 or error!=logged['latent_max_abs']:raise ValueError('Saved EMA GPU replay differs from stored outputs')
                    replay.append(dict(arm=arm,target_id=ident,latent_max_abs=error))
    if m['initial_path_sha256']!=sha(run/'initial_path.h5'):raise ValueError('Changed initial-path predictions')
    with h5py.File(run/'initial_path.h5') as f,h5py.File(c['baseline_predictions']) as old:
        if set(f)!=set(ids):raise ValueError('Incomplete initial-path control')
        for source in selected:
            ident=source['id'];item=items[ident];n=item['length'];z=f[ident+'/latent'][:];bb=f[ident+'/backbone'][:]
            if z.shape!=(4,n,8) or bb.shape!=(4,n,4,3) or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Invalid initial-path output')
            edit=editable_window(item['keep'][None],torch.ones(1,n,dtype=torch.bool),spec['flank'])[0].numpy()
            rows=raw_rows(bb,item['fragment'],item['start'],'initial_generated_cond',ident,item['family']);base=old['new/'+ident+'/backbone'][:]
            for k,r in enumerate(rows):
                scores=ca_metrics(bb[k,~edit,1],base[k,~edit,1]);records.append(dict(r,bucket=source['bucket'],scaffold_ca_rmsd=scores['ca_rmsd'],scaffold_ca_lddt=scores['ca_lddt']))
    arms=(*arms,'initial_generated_cond')
    initial_ids=[next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    initial_items=load_conditions(c['fragments'],initial_ids,'c20_center',cohort='train')
    if len(m['initial_controls'])!=4 or {r['target_id'] for r in m['initial_controls']}!=set(initial_ids) or len(m['checkpoint_replay'])!=2 or m['initial_predictions_sha256']!=sha(run/'initial_parent.h5'):raise ValueError('Changed initial/global or checkpoint controls')
    with h5py.File(run/'initial_parent.h5') as f,h5py.File(c['baseline_predictions']) as old:
        if set(f)!=set(initial_ids):raise ValueError('Changed all-edit control inventory')
        for ident in initial_ids:
            item=initial_items[ident];z=f[ident+'/latent'][:];bb=f[ident+'/backbone'][:];expected=old['new/'+ident+'/latent'][:]
            error=float(np.max(abs(z-expected)));scores=check_backbones(bb,old['new/'+ident+'/backbone'][:],item['fragment'],item['start'],ident);logged=next(r for r in m['initial_controls'] if r['target_id']==ident)
            if z.shape!=expected.shape or not np.isfinite(z).all() or error>1e-5 or error!=logged['latent_max_abs'] or any(scores[k]!=logged[k] for k in scores):raise ValueError('Initial wrapper changed parent output')
    summaries=[]
    for arm in arms:
        rr=[r for r in records if r['arm']==arm];summaries.append(dict(arm=arm,samples=len(rr),raw=sum(r['raw_gate_passed'] for r in rr),valid=sum(r['coarse_valid'] for r in rr),mean_motif_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr])),mean_scaffold_rmsd=float(np.mean([r['scaffold_ca_rmsd'] for r in rr])),mean_scaffold_lddt=float(np.mean([r['scaffold_ca_lddt'] for r in rr]))))
    lookup={r['arm']:r for r in summaries};improved=sum(sum(r['raw_gate_passed'] for r in records if r['target_id']==i and r['arm']=='generated_cond')>sum(r['raw_gate_passed'] for r in records if r['target_id']==i and r['arm']=='parent') for i in ids)
    gate=None
    if not c['profile_only']:
        gate=quality_gate(summaries,records,ids,spec)
    contrasts=[]
    if not c['profile_only']:
        rows={(r['arm'],r['target_id'],r['generation_slot']):r for r in records}
        for candidate,reference in [('generated_cond','parent'),('generated_cond','generated_null'),('generated_cond','initial_generated_cond'),('native_cond','native_null'),('native_cond','generated_cond')]:
            metrics={}
            for metric in ('raw_gate_passed','coarse_valid','motif_ca_rmsd'):
                metrics[metric]=clustered([np.mean([float(rows[candidate,i,k][metric])-float(rows[reference,i,k][metric]) for k in range(4)]) for i in ids])
            contrasts.append(dict(candidate=candidate,reference=reference,metrics=metrics))
    recommended=max(10,math.ceil((m['training_seconds']*spec['updates']/c['updates']*1.5+(m['elapsed_seconds']-m['training_seconds'])*10+120)/60)) if c['profile_only'] else None
    return dict(status='complete',scaffold_clock=True,profile_only=c['profile_only'],numerically_qualified=True,qualified=True if c['profile_only'] else gate['qualified'],manifest_path=str(mp.resolve()),manifest_sha256=sha(mp),protocol_sha256=sha(c['protocol']),fragments_sha256=sha(c['fragments']),checkpoint_sha256=m['checkpoint_sha256'],predictions_sha256=m['predictions_sha256'],updates=c['updates'],trainable_parameters=m['trainable_parameters'],training_seconds=m['training_seconds'],elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],controls=len(m['controls']),saved_ema_gpu_replay=replay,initial_global_controls=len(m['initial_controls']),prefix_max_abs=prefix_error,recommended_full_minutes=recommended,summary=summaries,refold_gate=gate,records=records,contrasts=contrasts,scope='Repeated training-only capacity diagnostic. Whole scaffold is free to move. Raw capacity does not establish same-refold designability. Native-context outputs are oracle controls; no model promotion.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1);d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Whole-chain scaffold-clock flow\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n');print(json.dumps({k:v for k,v in d.items() if k!='records'}))


if __name__=='__main__':main()
