import argparse,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads((a.runs[0]/'manifest.json').read_text());d=dict(status=m['status'],verified=len(m['records']),scope=m['scope'],error=m.get('error'))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text(f"# Teacher training source verification\n\nStatus: {d['status']}; verified {d['verified']} of 512 fixed families.\n\n{d['scope']}. Full sequence, complete N/CA/C/O backbone, unique residue mapping and cached CA RMSD below 0.02 Angstrom required.\n\n"+(d['error'] or '')+'\n')


if __name__=='__main__':main()
