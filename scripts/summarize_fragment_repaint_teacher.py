"""Independently audit all oracle completions before any teacher-label refolding."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from fragment_repaint_teacher_core import audit,eligibility
from evaluate_decoder_fragment_variance import check_backbones
from fragment_validation_core import raw_rows
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text()) if mp.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];spec=audit(c);hc=json.loads(Path(c['historical_manifest']).read_text())['config']
    expected_controls={('historical',i) for i in hc['control_ids']}|{('outside',next(r['id'] for r in c['selected'] if r['bucket']==b)) for b in (128,256,384,512)}
    if (m['training_updates_executed']!=0 or len(m['controls'])!=8 or {(r['kind'],r['target_id']) for r in m['controls']}!=expected_controls
            or len(m['batches'])!=32 or {r['target_id'] for r in m['batches']}!=set(c['target_ids'])
            or any(r['peak_reserved_GiB']>75 or r['seconds']<=0 for r in m['batches'])
            or m['predictions_sha256']!=sha(run/'predictions.h5')):raise ValueError('Changed teacher inventory/profile')
    oldrows=json.loads(Path(c['historical_selection']).read_text())['rows'];records=[];diversity=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['historical_predictions']) as old,h5py.File(c['historical_parent_predictions']) as hp,h5py.File(c['fragments']) as fr,h5py.File(c['baseline_predictions']) as base:
        if set(f)!={'historical','new'} or set(f['new'])!=set(c['target_ids']) or set(f['historical'])!=set(hc['control_ids']):raise ValueError('Changed saved coverage')
        for ident in hc['control_ids']:
            row=next(r for r in oldrows if r['target_id']==ident);n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;g=f['historical/'+ident]
            if g['latent'].shape!=(4,n,8) or g['backbone'].shape!=(4,n,4,3):raise ValueError('Bad historical shape')
            gap=float(np.max(abs(g['latent'][:]-hp['original50/motif_u3/'+ident+'/latent'][:])))
            check=check_backbones(g['backbone'][:],old[ident+'/full_control'][:],np.asarray(row['reference']['backbone'],np.float32)[st:st+k],st,ident)
            logged=next(r for r in m['controls'] if (r['kind'],r['target_id'])==('historical',ident))
            if not np.isfinite(gap) or gap>1e-5 or gap!=logged['latent_max_abs'] or any(check[k]!=logged[k] for k in check):raise ValueError('Historical audit failed')
        for row in c['selected']:
            ident=row['id'];n=row['length'];q=fr['train/'+ident+'/conditions/c20_center'];fragment=q['fragment'][:];st=int(q.attrs['start']);g=f['new/'+ident]
            target=np.zeros((4,n,8),np.float32);target[:,st:st+20]=fr['train/'+ident+'/reference_z'][st:st+20]
            if not np.array_equal(target,g['target'][:]) or g['latent'].shape!=(4,n,8) or g['backbone'].shape!=(4,n,4,3) or not np.isfinite(g['latent'][:]).all() or not np.isfinite(g['backbone'][:]).all():raise ValueError('Changed oracle inputs or outputs')
            if ('outside',ident) in expected_controls:
                if not np.array_equal(g['latent'][:],g['outside_control_latent'][:]) or not np.array_equal(g['backbone'][:],g['outside_control_backbone'][:]):raise ValueError('Scaffold target leakage')
            for arm,bb in [('oracle_repaint',g['backbone'][:]),('parent',base['new/'+ident+'/backbone'][:])]:
                rr=raw_rows(bb,fragment,st,arm,ident,row['family']);records.extend(dict(r,bucket=row['bucket']) for r in rr)
                keep=np.ones(n,bool);keep[st:st+20]=False
                for i in range(4):
                    for j in range(i+1,4):
                        scores=ca_metrics(bb[i,keep,1],bb[j,keep,1])
                        diversity.append(dict(arm=arm,target_id=ident,slots=[i,j],both_raw=rr[i]['raw_gate_passed'] and rr[j]['raw_gate_passed'],scaffold_ca_rmsd=scores['ca_rmsd']))
    summary=[]
    for arm in ('oracle_repaint','parent'):
        rr=[r for r in records if r['arm']==arm]
        summary.append(dict(arm=arm,samples=len(rr),raw=sum(r['raw_gate_passed'] for r in rr),valid=sum(r['coarse_valid'] for r in rr),mean_motif_rmsd=float(np.mean([r['motif_ca_rmsd'] for r in rr]))))
    if summary[1]['raw']!=25 or summary[1]['valid']!=128:raise ValueError('Parent decisions changed')
    families=sorted({r['family'] for r in records});rng=np.random.default_rng(2026100501);ix=rng.integers(0,len(families),(10000,len(families)));differences=[]
    for metric in ('raw_gate_passed','coarse_valid','motif_ca_rmsd'):
        delta=np.array([np.mean([r[metric] for r in records if r['family']==fam and r['arm']=='oracle_repaint'])-np.mean([r[metric] for r in records if r['family']==fam and r['arm']=='parent']) for fam in families])
        differences.append(dict(metric=metric,delta=float(delta.mean()),family_interval=np.quantile(delta[ix].mean(1),[.025,.975]).tolist()))
    return dict(status='complete',oracle_teacher=True,manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],protocol_sha256=sha(c['protocol']),
                controls=8,historical_samples=16,summary=summary,records=records,diversity=diversity,differences=differences,
                refold_eligibility=eligibility([r for r in records if r['arm']=='oracle_repaint']),generation_seconds=sum(r['seconds'] for r in m['batches']),
                elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in m['batches']),designability_tested=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0])
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Full-context RePaint teacher feasibility','',f"Status: {d['status']}."]
    if d['status']=='complete':
        lines+=['','Oracle training-label source, not isolated-fragment inference. All32 training proteins and128 outputs retained.','', '| Arm | Raw motif matches | Valid | Mean motif RMSD (A) |','|---|---:|---:|---:|']
        for r in d['summary']:lines.append(f"| {r['arm']} | {r['raw']}/128 | {r['valid']}/128 | {r['mean_motif_rmsd']:.3f} |")
        lines+=['',f"Eight control groups passed, including16 historical outputs. Generation {d['generation_seconds']:.2f}s; worker {d['elapsed_seconds']:.2f}s; peak {d['peak_reserved_GiB']:.2f}GiB.",f"Eligible for complete fixed-motif refolding: {d['refold_eligibility']['qualified']}. Designability not yet measured.",'','The teacher uses native-context motif codes. A better result cannot be attributed solely to architecture and would not prove an isolated-input student can reproduce it.']
        for r in d['differences']:lines.append(f"\nTeacher minus parent {r['metric']}: {r['delta']:+.4f};95% family interval {r['family_interval']}.")
    else:lines+=['',str(d.get('error'))]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:v for k,v in d.items() if k not in ('records','diversity')}))


if __name__=='__main__':main()
