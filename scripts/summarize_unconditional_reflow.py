"""Audit unconditional training schedules, frozen weights and raw evaluations."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from prepare_overfit import sha


def analyze(run):
    if not (run/'manifest.json').exists():return dict(status='failed',error='Missing startup manifest; see registered log')
    m=json.loads((run/'manifest.json').read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),updates=m['updates'])
    c=m['config'];recipe=json.loads(Path(c['protocol']).read_text());rows=json.loads(Path(c['selection']).read_text())['rows'];expected={(r['target_id'],k) for r in rows for k in range(4)}
    for key in ('protocol','labels_manifest','pairs','checkpoint','decoder_checkpoint','selection','generation_manifest','initial_manifest','initial_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if m['updates']!=c['updates'] or len(m['training'])!=c['updates'] or [r['step'] for r in m['training']]!=list(range(1,c['updates']+1)):raise ValueError('Incomplete training')
    if not m['frozen_names'] or m['frozen_initial']!=m['frozen_final']:raise ValueError('Frozen weight control failed')
    if any(not math.isfinite(r[k]) or (k=='gradient_norm' and r[k]<=0) for r in m['training'] for k in ('flow_loss','gradient_norm')):raise ValueError('Nonfinite loss/gradient')
    for r in m['training']:
        if r['length']!=recipe['lengths'][(r['step']-1)%8] or r['batch']!=c['batches'][str(r['length'])] or len(r['indices'])!=r['batch'] or len(set(r['indices']))!=len(r['indices']) or any(i<0 or i>=256 for i in r['indices']):raise ValueError('Invalid training draw')
    if len(m['initial_controls'])!=64 or {(r['target_id'],r['slot']) for r in m['initial_controls']}!=expected or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 or not r['validity_identical'] for r in m['initial_controls']):raise ValueError('Initial controls failed')
    steps=[0]+c['evaluation_steps']
    if [r['step'] for r in m['evaluations']]!=steps or len(m['sampling_controls'])!=len(steps)*4 or {(r['step'],r['target_id']) for r in m['sampling_controls']}!={(s,i) for s in steps for i in c['control_ids']} or any(r['latent_max_abs']>1e-5 for r in m['sampling_controls']):raise ValueError('Missing/failed sampling controls')
    summaries=[];gen=json.loads(Path(c['generation_manifest']).read_text());reference=Path(c['generation_manifest']).parent/'predictions.h5'
    for evaluation in m['evaluations']:
        step=evaluation['step'];scores=evaluation['scores']
        if len(scores)!=64 or {(r['target_id'],r['slot']) for r in scores}!=expected:raise ValueError('Incomplete raw evaluation')
        metrics=[]
        with h5py.File(run/f'evaluation_{step}.h5') as f,h5py.File(reference) as parent:
            if set(f)!={r['target_id'] for r in rows}:raise ValueError('Incomplete evaluation arrays')
            for row in rows:
                ident=row['target_id'];bb=f[ident]['backbone'][:];z=f[ident]['latent'][:];old=parent['original50/unconditional/'+ident+'/backbone'][:]
                if bb.shape!=(4,row['length'],4,3) or z.shape!=(4,row['length'],8) or not np.isfinite(bb).all() or not np.isfinite(z).all():raise ValueError('Invalid arrays')
                valid=backbone_geometry(bb)['coarse_valid'];logged=sorted([r for r in scores if r['target_id']==ident],key=lambda r:r['slot'])
                if not np.array_equal(valid,[r['coarse_valid'] for r in logged]):raise ValueError('Geometry audit failed')
                metrics.extend(ca_metrics(x[:,1],y[:,1]) for x,y in zip(bb,old))
        if step and not c['profile_only'] and not (run/f'ema_{step}.ckpt').is_file():raise ValueError('Missing saved EMA')
        summaries.append(dict(step=step,coarse_valid=float(np.mean([r['coarse_valid'] for r in scores])),ca_lddt_to_same_noise_teacher=float(np.mean([r['ca_lddt'] for r in metrics])),mean_rmsd_to_same_noise_teacher=float(np.mean([r['ca_rmsd'] for r in metrics])),raw_geometry_screen_passed=float(np.mean([r['coarse_valid'] for r in scores]))>=.98,seconds=evaluation['seconds']))
    train_seconds=sum(r['seconds'] for r in m['batches']);peak=max(r['peak_reserved_bytes'] for r in m['batches'])/2**30;eval_seconds=sum(r['seconds'] for r in m['evaluations']);overhead=max(0,m['elapsed_seconds']-train_seconds-eval_seconds);predicted=train_seconds/c['updates']*1000+max(r['seconds'] for r in m['evaluations'])*3+overhead
    return dict(status='complete',arm=c['arm'],profile_only=c['profile_only'],updates=c['updates'],max_reserved_gib=peak,train_seconds=train_seconds,projected1000_seconds=predicted,profile_qualified=bool(c['profile_only'] and c['updates']==40 and peak<70 and predicted<3480),summaries=summaries,manifest_sha256=sha(run/'manifest.json'),scope='Raw unconditional output; mapping fidelity is descriptive, not a generative accuracy gate. No designability or conditional-folding qualification.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Unconditional trajectory compression','',f"Status: {d['status']}."]
    if d['status']=='complete':
        lines+=['',f"Arm {d['arm']}, profile={d['profile_only']}, updates={d['updates']}. Training {d['train_seconds']:.2f}s, peak {d['max_reserved_gib']:.2f}GiB, projected1000updates including evaluation/startup {d['projected1000_seconds']:.1f}s. Profile qualified: {d['profile_qualified']}.",'','| Step | Raw coarse validity | CA-lDDT to same-noise original50 | Geometry screen |','|---|---:|---:|---|']
        for r in d['summaries']:lines.append(f"| {r['step']} | {r['coarse_valid']:.4f} | {r['ca_lddt_to_same_noise_teacher']:.4f} | {r['raw_geometry_screen_passed']} |")
        lines+=['',d['scope'],'','All64 outputs retained at every endpoint; unchanged original10 initial outputs, learned-null/generic CFG0 controls and frozen unused weights verified. Training labels contain no sequence inputs. Locked tests remain unscored.']
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
