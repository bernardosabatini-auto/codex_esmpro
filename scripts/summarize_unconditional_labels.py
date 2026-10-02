"""Audit all unconditional labels, including failed teacher geometry and noise identity."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.flow import target_noise
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha


def analyze(run):
    m=json.loads((run/'manifest.json').read_text())
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'))
    c=m['config']
    for key in ('protocol','parent_manifest','checkpoint','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if len(m['controls'])!=8 or {r['length'] for r in m['controls']}!=set(c['lengths']) or any(r['latent_max_abs']>1e-5 or r['ca_rmsd']>.01 or r['ca_lddt']<.999 for r in m['controls']):raise ValueError('Incomplete/failed controls')
    expected={(n,k) for n in c['lengths'] for k in range(0,c['samples'],c['batch'])}
    if {(r['length'],r['offset']) for r in m['batches']}!=expected or len(m['batches'])!=len(expected):raise ValueError('Incomplete batches')
    rows=[]
    with h5py.File(run/'pairs.h5') as f:
        if set(f)!=set(map(str,c['lengths'])):raise ValueError('Wrong length coverage')
        for n in c['lengths']:
            g=f[str(n)];noise=g['noise'][:];endpoint=g['endpoint'][:];bb=g['backbone'][:]
            if noise.shape!=(c['samples'],n,8) or endpoint.shape!=noise.shape or bb.shape!=(c['samples'],n,4,3) or not all(np.isfinite(x).all() for x in (noise,endpoint,bb)):raise ValueError('Invalid label shapes/values')
            for k in range(c['samples']):
                expected=target_noise([f'unconditional_train_length{n}'],[n],8,seed=c['seed'],sample_index=k)[0].numpy()
                if not np.array_equal(noise[k],expected):raise ValueError('Noise provenance mismatch')
            geometry=backbone_geometry(bb)
            if not np.array_equal(geometry['coarse_valid'],g['coarse_valid'][:]):raise ValueError('Invalid stored geometry')
            rows.append(dict(length=n,samples=len(bb),coarse_valid=float(geometry['coarse_valid'].mean())))
    return dict(status='complete',lengths=rows,total_labels=sum(r['samples'] for r in rows),generation_seconds=sum(r['seconds'] for r in m['batches']),max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/2**30,controls=m['controls'],pairs_sha256=sha(run/'pairs.h5'),manifest_sha256=sha(run/'manifest.json'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Unconditional teacher trajectory labels','',f"Status: {d['status']}."]
    if d['status']=='complete':
        lines += ['',f"All {d['total_labels']} Gaussian/endpoint/backbone triples retained, including failed coarse geometry. No sequence or experimental structure used as training input. Noise addresses differ from development generation. Generation {d['generation_seconds']:.2f}s, peak {d['max_reserved_gib']:.2f}GiB."]
        for r in d['lengths']:lines.append(f"- Length{r['length']}: {r['samples']} labels, coarse validity {r['coarse_valid']:.4f}.")
        lines += ['','Every Gaussian and geometry decision was independently audited. These are model-generated labels, not biological conformational populations. Training and designability are not yet qualified.']
    else:lines += ['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
