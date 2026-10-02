"""Audit generation coverage; geometry is not a designability qualification."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from generate_generative_pilot import motif_error
from latentfold.ensemble_metrics import backbone_geometry


def analyze(run):
    m=json.loads((run/'manifest.json').read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'),records=len(m['records']))
    c=m['config'];rows=json.loads(Path(c['selection']).read_text())['rows']
    for key in ('protocol','selection','panel','embedding_cache','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    expected={(h['name'],mode,r['target_id'],k) for h in c['heads'] for mode in c['modes'] for r in rows for k in range(c['samples'])}
    actual={(r['head'],r['mode'],r['target_id'],r['slot']) for r in m['records']}
    if actual!=expected or len(m['records'])!=len(expected):raise ValueError('Incomplete/duplicate generation')
    checks={(r['head'],r['target_id']) for r in m['controls']}
    if checks!={(h['name'],i) for h in c['heads'] for i in c['control_ids']} or len(checks)!=len(m['controls']):raise ValueError('Missing controls')
    if any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Failed control')
    batches={(r['head'],r['mode'],r['target_id']):r for r in m['batches']}
    if len(batches)!=len(m['batches']) or len(batches)*c['samples']!=len(expected):raise ValueError('Missing batch costs')
    summaries=[]
    with h5py.File(run/'predictions.h5') as f:
        for h in c['heads']:
            for mode in c['modes']:
                selected=[r for r in m['records'] if r['head']==h['name'] and r['mode']==mode]
                for row in rows:
                    ident=row['target_id'];g=f[h['name']+'/'+mode+'/'+ident];bb=g['backbone'][:];z=g['latent'][:]
                    if bb.shape!=(c['samples'],row['length'],4,3) or z.shape!=(c['samples'],row['length'],8) or not np.isfinite(bb).all() or not np.isfinite(z).all():raise ValueError('Bad arrays')
                    geom=backbone_geometry(bb)['coarse_valid'];errors=motif_error(bb,f['references/'+ident+'/backbone'][:],g['motif_mask'][:]);rec=sorted([r for r in selected if r['target_id']==ident],key=lambda r:r['slot'])
                    if not np.array_equal(geom,[r['coarse_valid'] for r in rec]) or not np.allclose(errors,[r['motif_drms'] for r in rec],atol=1e-7,rtol=0):raise ValueError('Metric audit failed')
                times=[r for r in m['batches'] if r['head']==h['name'] and r['mode']==mode]
                summaries.append(dict(head=h['name'],mode=mode,samples=len(selected),coarse_valid=float(np.mean([r['coarse_valid'] for r in selected])),motif_drms=float(np.mean([r['motif_drms'] for r in selected])),motif_under1A=float(np.mean([r['motif_drms']<=1 for r in selected])),generation_seconds=sum(r['seconds'] for r in times),peak_reserved_GiB=max(r['peak_reserved_bytes'] for r in times)/2**30))
    return dict(status='complete',summaries=summaries,controls=m['controls'],reference_roundtrips=m['references'],designability_tested=False,predictions_sha256=sha(run/'predictions.h5'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Unconditional and motif generation pilot','',f"Status: {d['status']}. Geometry is not designability. All failures retained; no generation retries."]
    if d['status']=='complete':
        lines+=['','| Head | Mode | N | Coarse valid | Motif dRMS A | Motif <=1A | Generation s | Peak GiB |','|---|---|---:|---:|---:|---:|---:|---:|']
        for r in d['summaries']:lines.append(f"| {r['head']} | {r['mode']} | {r['samples']} | {r['coarse_valid']:.4f} | {r['motif_drms']:.3f} | {r['motif_under1A']:.4f} | {r['generation_seconds']:.2f} | {r['peak_reserved_GiB']:.2f} |")
        lines+=['','FP32 generation only; unconditional path does not require ESM embeddings. Timings exclude loading, encoding reference motifs, numerical controls and disk I/O. Motif codes are extracted from complete reference structures and may encode scaffold context. Experimental positive controls and ProteinMPNN/refolding are still required. No same-sequence multistability, novelty, designability or general speed claim.']
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
