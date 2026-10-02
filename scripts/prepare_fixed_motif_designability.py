"""Preserve the original scaffold panel; provide only motif amino acids."""
import argparse,copy,json
from pathlib import Path
from prepare_overfit import sha
from prepare_fragment_designability import audit_inputs


def audit_fixed_inputs(c):
 audit_inputs(c)
 for key in ('baseline_manifest','selection'):
  if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
 baseline=json.loads(Path(c['baseline_manifest']).read_text());old=baseline['config'];rows={r['target_id']:r for r in json.loads(Path(c['selection']).read_text())['rows']}
 if baseline['status']!='complete':raise ValueError('Incomplete baseline')
 for key in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256','predictions','predictions_sha256','source_predictions_sha256','reference_predictions_sha256'):
  if c[key]!=old[key]:raise ValueError('Changed matched recipe '+key)
 if len(c['entries'])!=len(old['entries']):raise ValueError('Changed matched entries')
 for r,b in zip(c['entries'],old['entries']):
  if {k:v for k,v in r.items() if k not in ('fixed_start','fixed_sequence')}!=b:raise ValueError('Changed backbone entry')
  n=r['length'];k=max(8,int(.3*n));st=(n-k)//2;expected='' if r['head']=='experimental' else rows[r['target_id']]['sequence'][st:st+k]
  if r['fixed_sequence']!=expected or r['fixed_start']!=(0 if r['head']=='experimental' else st):raise ValueError('Incorrect supplied fragment sequence')


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];baseline=root/'runs/fragment_designability_49865077/manifest.json';m=json.loads(baseline.read_text());c=copy.deepcopy(m['config']);gm=json.loads(Path(c['generation_manifest']).read_text());selection=Path(gm['config']['selection']);rows={r['target_id']:r for r in json.loads(selection.read_text())['rows']}
 for r in c['entries']:
  n=r['length'];k=max(8,int(.3*n));st=(n-k)//2;r.update(fixed_start=0 if r['head']=='experimental' else st,fixed_sequence='' if r['head']=='experimental' else rows[r['target_id']]['sequence'][st:st+k])
 c.update(assay='fixed_motif',decision='Same20backbones; fix supplied motif residues only;160refolds; strict same-sequence motif retention')
 for key,path in [('protocol',root/'configs/fixed_motif_designability_protocol.json'),('baseline_manifest',baseline),('selection',selection)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
 audit_fixed_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen same20backbones with explicit motif sequence constraints')
if __name__=='__main__':main()
