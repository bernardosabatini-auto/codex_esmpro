"""Operational sequence-family groups for the reused 626-target development set."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import h5py

def main():
 p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--ids',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False);ids=a.ids.read_text().splitlines();query=a.output/'sequences.fasta'
 with h5py.File(a.dataset,'r') as h,query.open('w') as f:
  if set(ids)!=set(h['val']):raise ValueError('development target coverage differs')
  for name in ids:f.write(f">{name}\n{str(h['val'][name].attrs['sequence'])}\n")
 hits=a.output/'hits.tsv';mm='/n/holylabs/bsabatini_lab/Users/bsabatini/mmseqs/bin/mmseqs'
 cmd=[mm,'easy-search',str(query),str(query),str(hits),str(a.output/'tmp'),'-s','7.5','-e','1e-3','--max-seqs','10000','--threads','1','--split-memory-limit','4G','--format-output','query,target,fident,qcov,tcov','-v','1']
 subprocess.run(cmd,check=True);parent={n:n for n in ids}
 def root(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for line in hits.read_text().splitlines():
  q,t,identity,qcov,tcov=line.split()
  if float(identity)>=.3 and max(float(qcov),float(tcov))>=.5:parent[root(q)]=root(t)
 groups={n:root(n) for n in ids};result=dict(status='complete',clusters=groups,n_targets=len(ids),n_clusters=len(set(groups.values())),command=cmd,sequence_sha256=hashlib.sha256(query.read_bytes()).hexdigest(),note='Connected components of detected >=30% identity hits at >=50% coverage either direction; heuristic search, not a guarantee of remote-homology independence.')
 (a.output/'clusters.json').write_text(json.dumps(result,indent=2)+'\n');print(result['n_targets'],result['n_clusters'])
if __name__=='__main__':main()
