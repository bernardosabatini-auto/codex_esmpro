import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_isolated_motif import analyze

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=root/'runs/isolated_motif_49864561'
 if analyze(run)['status']!='complete':raise ValueError('Incomplete baseline')
 old=json.loads((run/'manifest.json').read_text())['config'];c=dict(samples=4,seed=old['seed'],control_ids=old['control_ids'],steps=50,repaint=3,update_history_each_eval=True,work_cap_seconds=480)
 for key,path in [('protocol',root/'configs/motif_history_protocol.json'),('parent_manifest',run/'manifest.json'),('parent_predictions',run/'predictions.h5'),('selection',Path(old['selection'])),('checkpoint',Path(old['checkpoint'])),('decoder_checkpoint',Path(old['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
 a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen64history-refresh samples and16baseline control samples')
if __name__=='__main__':main()
