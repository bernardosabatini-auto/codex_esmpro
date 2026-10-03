"""Replay every bounded correction decision and independently score endpoints."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from fragment_endpoint_core import audit_config,score,retract_numpy
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),refold_gate_passed=False)
    c=m['config'];spec=audit_config(c)
    if m['training_updates_executed'] or m['predictions_sha256']!=sha(run/'predictions.h5') or len(m['cases'])!=4 or {r['target_id'] for r in m['cases']}!=set(c['target_ids']):raise ValueError('Incomplete correction inventory')
    wanted={('historical',i,k) for i in c['target_ids'] for k in range(4)}|{(kind,i,0) for i in c['target_ids'] for kind in ('autograd_forward','finite_difference')}
    if len(m['controls'])!=24 or {(r['kind'],r['target_id'],r.get('slot',0)) for r in m['controls']}!=wanted or any(not r['passed'] for r in m['controls']):raise ValueError('Correction controls failed')
    for r in m['controls']:
        if r['kind']=='finite_difference' and ([x['eps'] for x in r['checks']]!=spec['finite_difference_eps'] or not any(abs(x['derivative']-r['analytic'])<=max(.01,.05*abs(r['analytic'])) for x in r['checks'])):raise ValueError('Invalid derivative evidence')
        if r['kind']=='autograd_forward' and (r['ca_rmsd']>.01 or r['ca_lddt']<.999):raise ValueError('Autograd parity failed')
    records=[];proposal_count=0;max_displacement=0.
    with h5py.File(run/'predictions.h5') as out,h5py.File(c['parent_predictions']) as parent,h5py.File(c['fragments']) as fragments:
        if set(out)!=set(c['target_ids']):raise ValueError('Changed case coverage')
        for ident in c['target_ids']:
            g=out[ident];q=fragments['development/'+ident+'/conditions/f30_center'];fragment=q['fragment'][:];st=int(q.attrs['start']);source=parent[spec.get('prediction_prefix','development/conditioned')+'/'+ident];reference=g['initial_latent'][:];current=reference.copy();bb=g['initial_backbone'][:];loss=g['initial_loss'][:];scale=np.sqrt(np.mean(reference**2,axis=(1,2)));initial=score(bb,fragment,st);archived=score(source['backbone'][:4],fragment,st)
            if not np.array_equal(reference,source['latent'][:4]) or not np.array_equal(g['fragment'][:],fragment) or int(g.attrs['start'])!=st or str(g.attrs['sequence'])!=str(q.attrs['sequence']):raise ValueError('Changed cached condition or latent')
            for k in range(4):
                metric=ca_metrics(bb[k,:,1],source['backbone'][k,:,1])
                if metric['ca_rmsd']>.2 or metric['ca_lddt']<.99 or any(initial[k][key]!=archived[k][key] for key in ('coarse_valid','raw_gate_passed')):raise ValueError('Initial cached parity failed')
            if np.max(np.abs(loss-np.array([.5*r['motif_ca_rmsd']**2 for r in initial])))>1e-6:raise ValueError('Initial objective differs')
            updates=g['updates'];indices=sorted(map(int,updates))
            if indices!=list(range(len(indices))) or len(indices)>spec['max_updates']:raise ValueError('Changed update budget')
            stalled=False
            for update in indices:
                ug=updates[str(update)];direction=ug['direction'][:];base=current.copy();remaining=np.sqrt(2*loss)>spec['desired_rmsd'];lines=sorted(int(k) for k in ug if k!='direction')
                if not remaining.any() or lines!=list(range(len(lines))) or not 1<=len(lines)<=4 or not np.isfinite(direction).all():raise ValueError('Invalid active update')
                any_accepted=False
                for line in lines:
                    if not remaining.any():raise ValueError('Proposal after all cases accepted')
                    pg=ug[str(line)];step=spec['line_search_steps'][line];z=pg['latent'][:];pb=pg['backbone'][:];pl=pg['loss'][:];distance=pg['relative_displacement'][:];accepted=pg['accepted'][:];proposal_count+=1
                    expected=retract_numpy(base-step*scale[:,None,None]*direction,reference);computed=np.sqrt(np.mean((z-reference)**2,axis=(1,2)))/scale
                    scored=score(pb,fragment,st);objectives=np.array([.5*r['motif_ca_rmsd']**2 for r in scored])
                    if pg.attrs['step']!=step or np.max(abs(z-expected))>1e-5 or np.max(abs(distance-computed))>1e-6 or np.max(abs(pl-objectives))>1e-6:raise ValueError('Proposal or objective changed')
                    if np.max(abs(z.mean(-1)-reference.mean(-1)))>1e-5 or np.max(abs(z.std(-1)-reference.std(-1)))>1e-5:raise ValueError('Latent row statistics changed')
                    decision=remaining&(distance<=spec['relative_radius'])&(pl<loss)
                    if spec.get('validity_guarded'):decision &= np.array([r['coarse_valid'] for r in scored])
                    if not np.array_equal(accepted,decision):raise ValueError('Not the first improving bounded proposal')
                    current=np.where(accepted[:,None,None],z,current);bb=np.where(accepted[:,None,None,None],pb,bb);loss=np.where(accepted,pl,loss);remaining &= ~accepted;any_accepted |= bool(accepted.any())
                if remaining.any() and len(lines)!=4:raise ValueError('Incomplete backtracking')
                stalled=not any_accepted
                if stalled and update!=indices[-1]:raise ValueError('Continued after deterministic stall')
            if len(indices)<spec['max_updates'] and (np.sqrt(2*loss)>spec['desired_rmsd']).any() and not stalled:raise ValueError('Early undeclared stopping')
            if not np.array_equal(current,g['guided_latent'][:]) or not np.array_equal(bb,g['guided_backbone'][:]) or not np.array_equal(loss,g['guided_loss'][:]):raise ValueError('Unrecorded endpoint change')
            displacement=np.sqrt(np.mean((current-reference)**2,axis=(1,2)))/scale;max_displacement=max(max_displacement,float(displacement.max()))
            if max_displacement>spec['relative_radius']+1e-6:raise ValueError('Trust region exceeded')
            final=score(bb,fragment,st)
            for k in range(4):records.append(dict(target_id=ident,family=str(g.attrs['family']),generation_slot=k,initial=initial[k],guided=final[k],relative_displacement=float(displacement[k])))
    if sum(r['proposal_calls'] for r in m['cases'])!=proposal_count or max(r['peak_reserved_bytes']/2**30 for r in m['cases'])>75:raise ValueError('Changed cost or memory accounting')
    newly_invalid=sum(r['initial']['coarse_valid'] and not r['guided']['coarse_valid'] for r in records);improved=sum(r['guided']['raw_gate_passed'] and r['initial']['motif_ca_rmsd']-r['guided']['motif_ca_rmsd']>=.2 for r in records);summaries={mode:dict(samples=16,valid=sum(r[mode]['coarse_valid'] for r in records),strict_raw=sum(r[mode]['raw_gate_passed'] for r in records),mean_proper_rmsd=float(np.mean([r[mode]['motif_ca_rmsd'] for r in records]))) for mode in ('initial','guided')}
    return dict(status='complete',manifest_sha256=sha(path),predictions_sha256=m['predictions_sha256'],controls=24,summaries=summaries,newly_invalid_samples=newly_invalid,qualified_improved_samples=improved,refold_gate_passed=bool(improved and newly_invalid<=(0 if spec.get('validity_guarded') else 1)),max_relative_displacement=max_displacement,proposal_batches=proposal_count,incremental_correction_seconds=sum(r['seconds'] for r in m['cases']),max_reserved_GiB=max(r['peak_reserved_bytes']/2**30 for r in m['cases']),records=records,scope='Four reused development families,16paired cached starts. Raw fit and latent-statistic preservation do not establish designability. Incremental correction time excludes cached parent generation; no end-to-end speed claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Bounded decoder correction\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')


if __name__=='__main__':main()
