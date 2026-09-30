"""Publish selection provenance and failure details, without evaluating models."""
import argparse,hashlib,json,math
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if len(a.runs)!=1:raise ValueError('one holdout run required')
 d=json.loads((a.runs[0]/'holdout.json').read_text())
 lines=['# Experimental holdout construction','',f"Status: {d['status']}.",'',
        'Selection uses no model scores. Inputs are full polymer sequences with explicit observed-residue maps; at least 90% of CA positions must be observed. Previously used training, benchmark and development chains are excluded.','',
        f"Training ID coverage audited across {len(d.get('coverage',[]))} caches. Inherited FASTA sequence content is spot-checked, 32 deterministic records per shard; it has not been re-extracted in full.",'',
        f"Recovered candidates: {len(d.get('candidates',[]))}; source rejections: {len(d.get('rejections',[]))}."]
 if d['status']=='complete':
  manifest=Path(d['locked_manifest']);raw=manifest.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=d['locked_sha256']:raise ValueError('locked manifest changed')
  locked=json.loads(raw);targets=locked['targets']
  if len(targets)!=d['selected_count'] or len(targets)<32:raise ValueError('incomplete locked target coverage')
  if len({r['id'] for r in targets})!=len(targets) or len({r['sequence_cluster'] for r in targets})!=len(targets):
   raise ValueError('duplicate target or sequence cluster')
  for r in targets:
   source=a.runs[0]/'mmcif'/f"{r['id'].split('_')[0]}.cif"
   checksum=hashlib.sha256()
   with source.open('rb') as handle:
    for block in iter(lambda:handle.read(1024*1024),b''):checksum.update(block)
   if checksum.hexdigest()!=r['source_sha256']:raise ValueError('native structure source changed')
   positions=r['observed_indices'];n=len(positions);length=len(r['sequence'])
   if not 50<=length<=512 or n<50 or n/length<.9 or positions!=sorted(set(positions)):
    raise ValueError('invalid full-sequence residue coverage')
   if len(r['ca_coords'])!=n or len(r['residue_map'])!=n or any(not 0<=i<length for i in positions):
    raise ValueError('residue correspondence length differs')
   if any(i+1!=m['label_seq_id'] for i,m in zip(positions,r['residue_map'])):
    raise ValueError('observed index does not match polymer position')
   if r['adjacent']!=[b==a+1 for a,b in zip(positions,positions[1:])]:raise ValueError('adjacency differs')
   if any(len(x)!=3 or not all(math.isfinite(v) for v in x) for x in r['ca_coords']):raise ValueError('invalid coordinates')
  lengths=[len(r['sequence']) for r in targets];short=sum(n<=256 for n in lengths)
  lines += ['',f"Locked targets: {len(targets)}; manifest SHA256: `{d['locked_sha256']}`.",
     f"Full input lengths {min(lengths)}–{max(lengths)}; {short} targets at ≤256 residues and {len(targets)-short} at 257–512. Minimum observed CA fraction {min(len(r['observed_indices'])/len(r['sequence']) for r in targets):.3f}.",
     f"Homology exclusions: {d['homology_exclusions']}. MMseqs2 heuristic search at sensitivity 7.5, rejecting ≥30% identity at ≥50% coverage in either direction. One representative per observed connected sequence cluster.",
     'Manifest/source hashes, target/cluster uniqueness, finite coordinates, residue maps and adjacency verified. This is a small operationally independent test relative to the audited exclusion corpus, not a guarantee against remote homology.',
     'Selection computes no model scores. Independent confirmation must use the full polymer inputs and explicit observed-residue maps.',
     'Unknown overlap with pretraining data for frozen ESMC, ProteinAE and the external comparator remains; this is not a claim of independence from pretraining.']
 else:lines+=['',f"Failure: {d.get('error','unfinished')}. No final test has been locked."]
 a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
