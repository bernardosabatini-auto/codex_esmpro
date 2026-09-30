import argparse,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
manifest=a.runs[0]/'manifest.json';d=json.loads(manifest.read_text());r=d['records']
lines=['# Verified pilot training data','',f"Status: {d['status']}; {len(r)} records.",f"Manifest SHA256: `{hashlib.sha256(manifest.read_bytes()).hexdigest()}`.",'',
       'Fixed hash-based selection from inherited training splits, balanced across four length buckets. All sequence identities, CA coordinate correspondence and residue numbering are checked against source AFDB PDBs. Confidence is retained without filtering. These references are AlphaFold predictions, not experimental structures.']
if d['status']=='complete':lines+=['',f"Largest source/cache CA RMSD: {max(x['source_ca_rmsd'] for x in r):.6f} Å.",f"Mean source pLDDT: {np.mean([x['mean_plddt'] for x in r]):.2f}; fraction of proteins below 80: {np.mean([x['mean_plddt']<80 for x in r]):.3f}."]
else:lines += [f"Failure: {d.get('error','unfinished')}"]
a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
