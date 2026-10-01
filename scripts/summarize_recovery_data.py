"""Publish aggregate coverage of the expanded, cached latent-only training pool."""
import argparse,hashlib,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.runs[0]/'manifest.json';d=json.loads(path.read_text())
    lines=['# Recovery training data','',f"Status: {d['status']}; verified records: {len(d['records'])}.",'',
        f"Manifest SHA256: `{hashlib.sha256(path.read_bytes()).hexdigest()}`.",'',d['selection'],
        'Existing training caches only; no new ESM computation or structure downloads. Original pilot records are checked for exact array equality. Expanded records have sequence, shape and finite-array checks; new native residue maps have not been recovered. Use for latent-only training.',
        f"Length-bucket counts: {d.get('selected_counts',{})}."]
    if d.get('error'):lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
