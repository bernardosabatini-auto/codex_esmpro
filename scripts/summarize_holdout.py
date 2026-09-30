"""Publish selection provenance and failure details, without evaluating models."""
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if len(a.runs)!=1:raise ValueError('one holdout run required')
 d=json.loads((a.runs[0]/'holdout.json').read_text())
 lines=['# Experimental holdout construction','',f"Status: {d['status']}.",'',
        'Selection uses no model scores. Inputs are full polymer sequences with explicit observed-residue maps; at least 90% of CA positions must be observed. Previously used training, benchmark and development chains are excluded.','',
        f"Training ID coverage audited across {len(d.get('coverage',[]))} caches. Inherited FASTA sequence content is spot-checked, 32 deterministic records per shard; it has not been re-extracted in full.",'',
        f"Recovered candidates: {len(d.get('candidates',[]))}; source rejections: {len(d.get('rejections',[]))}."]
 if d['status']=='complete':lines += ['',f"Locked targets: {d['selected_count']}; manifest SHA256: `{d['locked_sha256']}`.",
     f"Homology exclusions: {d['homology_exclusions']}. MMseqs2 heuristic search at sensitivity 7.5, rejecting ≥30% identity at ≥50% coverage in either direction. One representative per observed connected sequence cluster.",
     'Unknown overlap with pretraining data for the frozen ESMC and ProteinAE remains; this is not a claim of independence from pretraining.']
 else:lines+=['',f"Failure: {d.get('error','unfinished')}. No final test has been locked."]
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
