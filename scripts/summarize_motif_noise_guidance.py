"""Audit every motif-noise proposal and frozen motif-only random-start selection."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from latentfold.flow import target_noise


def motif_score(bb,fragment):
    n=bb.shape[-3];k=len(fragment);st=(n-k)//2;x=bb[...,st:st+k,1,:];y=fragment[:,1]
    dx=np.linalg.norm(x[..., :,None,:]-x[...,None,:,:],axis=-1);dy=np.linalg.norm(y[:,None]-y[None,:],axis=-1)
    return np.sqrt(np.mean((dx-dy)**2,axis=(-2,-1)))


def analyze(run):
    if not (run/'manifest.json').exists():return dict(status='failed',error='Missing startup manifest',controls=[])
    m=json.loads((run/'manifest.json').read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),controls=m['controls'],completed_cases=len(m['cases']))
    c=m['config'];expected={(i,k) for i in c['target_ids'] for k in range(2)}
    for key in ('protocol','parent_manifest','parent_predictions','selection','checkpoint','decoder_checkpoint','fragment_manifest','fragment_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if len(m['cases'])!=8 or {(r['target_id'],r['slot']) for r in m['cases']}!=expected:raise ValueError('Incomplete cases')
    controls=m['controls']
    for kind,count in [('forward',8),('ad_forward',4),('finite_difference',4),('gradient_checkpoint',1)]:
        rows=[r for r in controls if r['kind']==kind]
        if len(rows)!=count:raise ValueError('Incomplete controls '+kind)
        keys={(r['target_id'],r.get('slot',0)) for r in rows}
        wanted=expected if kind=='forward' else ({(c['target_ids'][0],0)} if kind=='gradient_checkpoint' else {(i,0) for i in c['target_ids']})
        if keys!=wanted:raise ValueError('Incorrect control coverage '+kind)
        for r in rows:
            if kind in ('forward','ad_forward') and (r['latent_max_abs']>1e-5 or r['ca_rmsd']>(.2 if kind=='forward' else .01) or r['ca_lddt']<(.99 if kind=='forward' else .999)):raise ValueError('Forward control failed')
            if kind=='forward' and not r['validity_identical']:raise ValueError('Initial geometry changed')
            if kind=='finite_difference' and (not r['passed'] or not any(x['absolute_error']<=max(.01,.05*abs(r['analytic'])) for x in r['checks'])):raise ValueError('Finite difference failed')
            if kind=='gradient_checkpoint' and r['relative_l2']>1e-4:raise ValueError('Checkpoint gradient failed')
    diversity=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['fragment_predictions']) as fragments,h5py.File(c['parent_predictions']) as source:
        for r in m['cases']:
            ident,k=r['target_id'],r['slot'];fragment=fragments[ident+'/fragment'][:];score=lambda bb:motif_score(bb,fragment);g=f[f'{ident}/{k}'];initial=g['initial'][:];guided=g['guided'][:];random=g['random_all'][:];chosen=g['random_selected'][:]
            if initial.shape!=(r['length'],4,3) or guided.shape!=initial.shape or random.shape!=(33,*initial.shape) or not all(np.isfinite(x).all() for x in (initial,guided,random)):raise ValueError('Invalid generated arrays')
            d=score(random);index=int(np.argmin(d))
            if index!=r['random_selected_index'] or not np.array_equal(chosen,random[index]) or not np.array_equal(random,source[f'{ident}/{k}/random_all'][:]):raise ValueError('Wrong random selection')
            choice=next(x for x in c['choices'] if (x['target_id'],x['slot'])==(ident,k))
            if choice['index']!=index or abs(choice['motif_drms']-d[index])>1e-4 or r['initial_seconds']!=choice['search_seconds']:raise ValueError('Changed frozen start')
            parent_record=next(x for x in json.loads(Path(c['parent_manifest']).read_text())['cases'] if (x['target_id'],x['slot'])==(ident,k))
            if choice['search_seconds']!=parent_record['initial_seconds']+parent_record['random_seconds']:raise ValueError('Changed source cost')
            for mode,bb in [('initial',initial),('guided',guided),('random',chosen)]:
                if abs(float(score(bb))-r[mode+'_distance'])>1e-4 or bool(backbone_geometry(bb[None])['coarse_valid'][0])!=r[mode+'_coarse_valid']:raise ValueError('Stored outcome audit failed')
            proposals=[x for x in m['proposals'] if (x['target_id'],x['slot'])==(ident,k)];iterations=[x for x in m['iterations'] if (x['target_id'],x['slot'])==(ident,k)]
            if len(iterations)>12:raise ValueError('Too many optimization updates')
            if len(proposals)!=r['line_search_proposals'] or len(iterations)!=r['gradient_evaluations'] or len(g['proposals'])!=len(proposals) or len(g['iterates'])!=len(iterations):raise ValueError('Missing optimization attempts')
            expected_noise=target_noise([ident],[r['length']],8,seed=c['generation_seed'] if index==0 else c['search_seed'],sample_index=k if index==0 else index-1,stream='flow:0' if index==0 else f'flow_search:{k}')[0].numpy()
            if not np.array_equal(g['initial_noise'][:],expected_noise):raise ValueError('Wrong selected initial Gaussian')
            previous=initial;previous_noise=g['initial_noise'][:];radius=np.linalg.norm(previous_noise);current_loss=.5*float(score(initial))**2
            for update,iteration in enumerate(iterations):
                trials=[x for x in proposals if x['update']==update]
                if not trials or len(trials)>4 or [x['trial'] for x in trials]!=list(range(len(trials))):raise ValueError('Invalid line search')
                accepted=False
                for j,x in enumerate(trials):
                    bb=g['proposals'][str(x['index'])][:];actual=float(score(bb));loss=.5*actual**2
                    if abs(actual-x['distance'])>1e-4 or abs(loss-x['loss'])>1e-4 or x['alpha']!=c['line_search_steps'][j]:raise ValueError('Proposal audit failed')
                    if x['accepted']:
                        if accepted or j!=len(trials)-1 or loss>current_loss+1e-4:raise ValueError('Nonmonotone/late proposal selected')
                        accepted=True;previous=bb;current_loss=loss
                it=g['iterates'][str(update)];noise=it['noise'][:]
                if not np.array_equal(it['backbone'][:],previous) or abs(np.linalg.norm(noise)/radius-1)>1e-5 or iteration['accepted']!=accepted:raise ValueError('Invalid accepted iterate')
                if not accepted and not np.array_equal(noise,previous_noise):raise ValueError('Rejected step changed noise')
                previous_noise=noise
            if not np.array_equal(guided,previous) or not np.array_equal(g['guided_noise'][:],previous_noise):raise ValueError('Wrong final iterate')
        for mode,dataset in [('initial','initial'),('guided','guided'),('random','random_selected')]:
            pairs=[dict(target_id=i,**ca_metrics(f[f'{i}/0/{dataset}'][:,1],f[f'{i}/1/{dataset}'][:,1])) for i in c['target_ids']]
            diversity.append(dict(mode=mode,pairs=pairs,mean_pairwise_ca_lddt=float(np.mean([r['ca_lddt'] for r in pairs]))))
    summaries=[]
    for mode in ('initial','guided'):
        rows=m['cases'];success=np.array([r[mode+'_distance']<=1 for r in rows]);valid=np.array([r[mode+'_coarse_valid'] for r in rows]);seconds=sum(r['initial_seconds']+(r[mode+'_seconds'] if mode!='initial' else 0) for r in rows)
        summaries.append(dict(mode=mode,cases=8,mean_distance=float(np.mean([r[mode+'_distance'] for r in rows])),motif_success=float(success.mean()),coarse_valid=float(valid.mean()),joint_motif_geometry=float((success&valid).mean()),seconds=seconds))
    return dict(status='complete',summaries=summaries,diversity=diversity,cases=m['cases'],controls=controls,max_guided_GiB=max(r['guided_peak_GiB'] for r in m['cases']),predictions_sha256=sha(run/'predictions.h5'),designability_tested=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Motif steering through initial noise','',f"Status: {d['status']}."]
    if d['status']=='complete':
        lines+=['','All8fixed cases retained. Each starts from its closest motif among33archived random candidates. Original50-step flow,FP32AE3,frozen weights. Motif distance-matrix RMS<=1A. Only fragment coordinates enter the objective; no geometry filtering.','', '| Method | Mean motif dRMS A | Motif success | Coarse valid | Joint motif/geometry | Seconds |','|---|---:|---:|---:|---:|---:|']
        for r in d['summaries']:lines.append(f"| {r['mode']} | {r['mean_distance']:.3f} | {r['motif_success']:.3f} | {r['coarse_valid']:.3f} | {r['joint_motif_geometry']:.3f} | {r['seconds']:.2f} |")
        lines += ['',f"Guided peak reserved memory {d['max_guided_GiB']:.2f}GiB. Numerical checks and all saved proposals/accepted states audited.",'','Times charge both methods the actual archived33draw generation cost; guided also includes optimization,transfers and controller decisions. Excludes loading,numerical controls,disk I/O and CPU candidate-selection time, recorded separately in config. Candidates reused rather than regenerated for benchmarking; no new end-to-end speed claim. Fixed radius does not establish an unchanged prior or designability. Strict fixed-motif ProteinMPNN/refolding and positive controls remain required. Only supplied fragment coordinates; no locked tests.']
        lines+=['','Across the two fixed seeds per family (four pairs per method), mean pairwise CA-lDDT: '+str({r['mode']:r['mean_pairwise_ca_lddt'] for r in d['diversity']})+'. This describes all outputs, not designable diversity.']
    else:lines+=['',d['error'],'',json.dumps(d['controls'],indent=2)]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
