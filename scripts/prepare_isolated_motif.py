import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_generative_pilot import analyze

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=root/'runs/generative_pilot_49855378'
 if analyze(run)['status']!='complete':raise ValueError('Invalid parent')
 old=json.loads((run/'manifest.json').read_text())['config'];head=next(h for h in old['heads'] if h['name']=='original50');c=dict(samples=4,seed=old['seed'],control_ids=old['control_ids'],work_cap_seconds=780)
 for key,path in [('protocol',root/'configs/isolated_motif_protocol.json'),('parent_manifest',run/'manifest.json'),('parent_predictions',run/'predictions.h5'),('selection',Path(old['selection'])),('checkpoint',Path(head['checkpoint'])),('decoder_checkpoint',Path(old['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
 a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen16isolated motifs/four seeds')
if __name__=='__main__':main()
