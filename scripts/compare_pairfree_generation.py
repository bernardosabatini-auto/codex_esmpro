"""Require historical original-output parity before interpreting pair-free generation."""
import argparse,json
from pathlib import Path
import h5py,numpy as np,torch
from summarize_generative_pilot import analyze
from audit_distill_labels import metrics
from latentfold.teacher_states import paired_change
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1)
    report=analyze(a.run)
    if report['status']!='complete':raise ValueError('Generation incomplete')
    m=json.loads((a.run/'manifest.json').read_text());old=json.loads((a.baseline/'manifest.json').read_text());c=m['config'];b=old['config']
    if old['status']!='complete' or [h['name'] for h in c['heads']]!=['original50','pairfree50'] or c['modes']!={'unconditional':1}:raise ValueError('Wrong paired generation scope')
    for key in ('seed','samples','selection_sha256','decoder_checkpoint_sha256','embedding_cache_sha256'):
        if c[key]!=b[key]:raise ValueError('Historical control recipe changed')
    if c['heads'][0]!=next(h for h in b['heads'] if h['name']=='original50'):raise ValueError('Historical original checkpoint changed')
    for h in c['heads']:
        if h['steps']!=50 or sha(h['checkpoint'])!=h['checkpoint_sha256']:raise ValueError('Checkpoint changed')
        if h.get('metadata_sha256') and sha(h['checkpoint']+'.meta.json')!=h['metadata_sha256']:raise ValueError('Pair-free metadata changed')
    rows=json.loads(Path(c['selection']).read_text())['rows'];families={r['target_id']:r['family'] for r in rows};controls=[]
    with h5py.File(a.run/'predictions.h5') as fresh,h5py.File(a.baseline/'predictions.h5') as prior:
        for ident in families:
            path='original50/unconditional/'+ident;bb=torch.from_numpy(fresh[path+'/backbone'][:]);reference=torch.from_numpy(prior[path+'/backbone'][:]);v=metrics(bb,reference);dz=float(np.max(abs(fresh[path+'/latent'][:]-prior[path+'/latent'][:])));r=dict(target_id=ident,latent_max_abs=dz,max_ca_rmsd=float(v['ca_rmsd'].max()),min_ca_lddt=float(v['ca_lddt'].min()))
            if dz>1e-5 or r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99:raise ValueError('Original archived output parity failed')
            controls.append(r)
    values={h:{i:float(np.mean([r['coarse_valid'] for r in m['records'] if r['head']==h and r['target_id']==i])) for i in families} for h in ('original50','pairfree50')};difference=paired_change(values['pairfree50'],values['original50'],families=families)
    times={h:sum(r['seconds'] for r in m['batches'] if r['head']==h) for h in values};report.update(validity_difference=difference,original_archive_controls=controls,generation_seconds=times,generation_speed_ratio=times['original50']/times['pairfree50'],worker_elapsed_seconds=m['elapsed_seconds'],manifest_sha256=sha(a.run/'manifest.json'),baseline_manifest_sha256=sha(a.baseline/'manifest.json'))
    lines=['# Corrected pair-free unconditional generation','', 'Same16development families/four noises,FP32/Euler50/AE3. All128outputs audited and64original samples matched to the historical archive. No designability or inference-pipeline speed claim.','','| Head | Valid /64 | Generation seconds | Peak reserved GiB |','|---|---:|---:|---:|']
    for r in report['summaries']:lines.append(f"| {r['head']} | {round(r['coarse_valid']*64)}/64 | {r['generation_seconds']:.2f} | {r['peak_reserved_GiB']:.2f} |")
    lines+=['',f"Pair-free minus original validity: {difference['difference']:+.5f},95%family interval {difference['ci95']}.",'',f"Generation-only original/pair-free time ratio: {report['generation_speed_ratio']:.3f}. One pass per head, not a repeated matched latency benchmark. Excludes loading, reference encoding, controls and writes. Unconditional sampling already skips sequence-conditioned pair computation.",'','The zero-width paired validity interval reflects zero observed failures in both small panels; it is not proof of population equivalence. Corrected r4b checkpoint, not either earlier confounded pair-free run. These are separately trained models; noise is paired, training seeds are not. Geometry alone cannot qualify useful proteins; a matched ProteinMPNN/refolding assay would remain required.']
    a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
