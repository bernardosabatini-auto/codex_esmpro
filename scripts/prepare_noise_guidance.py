"""Freeze the existing profile families and original checkpoint for noise steering."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_generative_pilot import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/noise_guidance_protocol.json';recipe=json.loads(protocol.read_text());run=root/recipe['parent_run']
    if analyze(run)['status']!='complete':raise ValueError('Invalid parent generation')
    m=json.loads((run/'manifest.json').read_text());old=m['config'];head=next(h for h in old['heads'] if h['name']=='original50');rows=json.loads(Path(old['selection']).read_text())['rows'];ids=old['control_ids']
    if len(ids)!=4 or {r['target_id'] for r in rows if r['target_id'] in ids}!=set(ids):raise ValueError('Missing profile families')
    c=dict(target_ids=ids,samples=2,generation_seed=old['seed'],search_seed=2026100217,steps=50,max_updates=12,line_search_steps=[.05,.025,.0125,.00625],finite_difference_eps=[.01,.001,.0001],random_samples=32,random_batch=8,work_cap_seconds=1080)
    for key,path in [('protocol',protocol),('parent_manifest',run/'manifest.json'),('parent_predictions',run/'predictions.h5'),('selection',Path(old['selection'])),('checkpoint',Path(head['checkpoint'])),('decoder_checkpoint',Path(old['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen8contact-steering cases')

if __name__=='__main__':main()
