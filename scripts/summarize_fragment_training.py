"""Independently recompute every raw fragment score, retaining all failures."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from generate_generative_pilot import motif_error
from prepare_overfit import sha


def interval(values):
    x=np.asarray(values,float);rng=np.random.default_rng(2026100233);means=x[rng.integers(0,len(x),(10000,len(x)))].mean(1)
    return dict(mean=float(x.mean()),ci95=np.quantile(means,[.025,.975]).tolist(),families=len(x))


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),updates=m.get('updates',0),profile_qualified=False)
    c=m['config']
    for key in ('protocol','data_report','data_manifest','fragments','checkpoint','decoder_checkpoint','initial_manifest','initial_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if c.get('variant')=='geometry':
        if sha(c['geometry_protocol'])!=c['geometry_protocol_sha256'] or len(m['geometry_controls'])!=(8 if c.get('distance_precision')=='fp64' else 4)*(len(c['evaluation_steps'])+1) or any(r['pose_latent_max_abs']>1e-4 for r in m['geometry_controls']):raise ValueError('Geometry conditioner controls failed')
    if c.get('distance_precision')=='fp64':
        if sha(c['geometry_precision_protocol'])!=c['geometry_precision_protocol_sha256'] or sha(c['pose_diagnostic_report'])!=c['pose_diagnostic_report_sha256']:raise ValueError('Changed precision correction evidence')
    if c.get('auxiliary_motif'):
        if sha(c['motif_objective_protocol'])!=c['motif_objective_protocol_sha256'] or sha(c['motif_baseline_report'])!=c['motif_baseline_report_sha256']:raise ValueError('Changed objective provenance')
        rows=m['motif_objective_updates']
        if len(rows)!=c['updates'] or [r['step'] for r in rows]!=list(range(1,c['updates']+1)) or any(not np.isfinite(r['motif_mse']) or r['aux_to_flow_ratio']>c['auxiliary_motif']['maximum_gradient_ratio']+1e-7 or r['flow_parameter_grad_norm']<=0 for r in rows):raise ValueError('Incomplete/unbounded motif gradients')
        if sum(r['motif_examples'] for r in rows)<c['updates'] or not any(r['aux_parameter_grad_norm']>0 for r in rows):raise ValueError('Insufficient motif objective exposure')
    if m['updates']!=c['updates'] or len(m['training'])!=c['updates'] or m['frozen_initial']!=m['frozen_final']:raise ValueError('Incomplete/frozen-weight failure')
    if [r['step'] for r in m['training']]!=list(range(1,c['updates']+1)) or any(not np.isfinite(r['flow_loss']) or r['adapter_gradient_norm']<=0 for r in m['training']):raise ValueError('Invalid training trace')
    if any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in m['initial_controls']):raise ValueError('Failed initial controls')
    if len(m['initial_controls'])!=(32 if c['profile_only'] else 128) or len(m['sampling_controls'])!=4 or any(r['original_max_abs']>1e-5 or r['batched_max_abs']>1e-4 for r in m['sampling_controls']):raise ValueError('Incomplete sampler controls')
    summaries=[];audited=0
    with h5py.File(c['fragments']) as src,h5py.File(c['initial_predictions']) as initial:
        expected={(cohort,mode,ident,k) for cohort in ('train','development') for ident in src[cohort] for mode in ('conditioned','null') for k in range(4) if not c['profile_only'] or cohort=='development' and ident in c['control_ids']}
        if [e['step'] for e in m['evaluations']]!=[0]+c['evaluation_steps']:raise ValueError('Missing evaluation')
        for e in m['evaluations']:
            index={(r['cohort'],r['mode'],r['target_id'],r['slot']):r for r in e['scores']}
            if set(index)!=expected or len(index)!=len(e['scores']):raise ValueError('Missing/duplicate outputs')
            diversity={}
            with h5py.File(run/f"evaluation_{e['step']}.h5") as f:
                for cohort,mode,ident in sorted({key[:3] for key in expected}):
                    g=src[cohort+'/'+ident];q=g['conditions/f30_center'];ref=g['reference_backbone'][:] if cohort=='train' else initial['references/'+ident+'/backbone'][:];bb=f[f'{cohort}/{mode}/{ident}/backbone'][:];z=f[f'{cohort}/{mode}/{ident}/latent'][:];fragment=q['fragment'][:];st=int(q.attrs['start']);k=len(fragment)
                    if bb.shape!=(4,len(ref),4,3) or z.shape!=(4,len(ref),8) or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Invalid saved output')
                    geom=backbone_geometry(bb);err=motif_error(bb[:,st:st+k],fragment,np.ones(k,bool));diversity[(cohort,mode,ident)]=float(np.mean([ca_metrics(bb[i,:,1],bb[j,:,1])['ca_rmsd'] for i in range(4) for j in range(i)]))
                    for slot in range(4):
                        old=index[(cohort,mode,ident,slot)];metrics=ca_metrics(bb[slot,:,1],ref[:,1])
                        if abs(old['motif_drms']-err[slot])>1e-6 or old['coarse_valid']!=int(geom['coarse_valid'][slot]) or any(abs(old[key]-value)>1e-6 for key,value in metrics.items()):raise ValueError('Saved-score mismatch')
                        if cohort=='development' and (e['step']==0 or c['arm']=='adapter_only' and mode=='null'):
                            original=initial['original50/unconditional/'+ident+'/backbone'][slot];control=ca_metrics(bb[slot,:,1],original[:,1])
                            if control['ca_rmsd']>.2 or control['ca_lddt']<.99 or np.max(abs(z[slot]-initial['original50/unconditional/'+ident+'/latent'][slot]))>1e-5:raise ValueError('Saved historical parity failed')
                        audited+=1
            for cohort in sorted({key[0] for key in expected}):
                families=sorted({r['family'] for r in e['scores'] if r['cohort']==cohort});arms={};paired=[]
                for mode in ('conditioned','null'):
                    rows=[r for r in e['scores'] if (r['cohort'],r['mode'])==(cohort,mode)];arms[mode]=dict(samples=len(rows),raw_valid_fraction=float(np.mean([r['coarse_valid'] for r in rows])),motif_fraction_under_1A=float(np.mean([r['motif_drms']<=1 for r in rows])),joint_fraction=float(np.mean([r['coarse_valid'] and r['motif_drms']<=1 for r in rows])),mean_motif_drms=float(np.mean([r['motif_drms'] for r in rows])),mean_reference_ca_lddt=float(np.mean([r['ca_lddt'] for r in rows])),mean_pairwise_sample_ca_rmsd=float(np.mean([v for (co,mo,_),v in diversity.items() if (co,mo)==(cohort,mode)])))
                for family in families:
                    means=[np.mean([r['coarse_valid'] and r['motif_drms']<=1 for r in e['scores'] if (r['cohort'],r['mode'],r['family'])==(cohort,mode,family)]) for mode in ('conditioned','null')];paired.append(means[0]-means[1])
                summaries.append(dict(step=e['step'],cohort=cohort,arms=arms,conditioned_minus_null_joint=interval(paired)))
    memory=max(b['peak_reserved_bytes']/2**30 for b in m['batches']);gate=next((r['conditioned_minus_null_joint']['ci95'][0]>0 for r in summaries if r['step']==2000 and r['cohort']=='train'),False)
    return dict(status='complete',config=c,manifest_sha256=sha(path),updates=m['updates'],audited_predictions=audited,training_seconds=sum(b['seconds'] for b in m['batches']),evaluation_seconds=sum(e['seconds'] for e in m['evaluations']),elapsed_seconds=m['elapsed_seconds'],max_reserved_GiB=memory,profile_qualified=c['profile_only'] and memory<=75,capacity_gate_passed=gate,summaries=summaries,initial_controls=len(m['initial_controls']),sampling_controls=len(m['sampling_controls']))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');view={k:v for k,v in d.items() if k!='config'};a.output.with_suffix('.md').write_text('# Explicit isolated-fragment conditioning\n\nRaw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.\n\n```json\n'+json.dumps(view,indent=2)+'\n```\n')

if __name__=='__main__':main()
