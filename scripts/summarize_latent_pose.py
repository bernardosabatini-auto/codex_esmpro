import argparse,json
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':
        if len(m['rows'])!=16:raise ValueError('incomplete pose diagnostic')
        d.update(summaries={name:{key:float(np.mean([r[name][key] for r in m['rows']])) for key in ('latent_rmse','reconstruction_rmsd')} for name in ('raw','canonical')},translation_max_difference=max(r['translation_latent_max_difference'] for r in m['rows']),canonical_coordinate_max_difference=max(r['canonical_coordinate_max_difference'] for r in m['rows']))
    else:d['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# ProteinAE latent pose diagnostic','',f"Status: {d['status']}.",'','Sixteen training structures, eight proper rotations and translations. These inputs describe the same conformation. Canonical coordinates use the first residue N/CA/C frame. Decoder noise is fixed across rotations.','', '| Encoder input | Latent RMSE across poses | Decoded CA RMSD to source (A) |','|---|---:|---:|']
    for name,r in d.get('summaries',{}).items():lines.append(f"| {name} | {r['latent_rmse']:.6f} | {r['reconstruction_rmsd']:.4f} |")
    if 'error' in d:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
