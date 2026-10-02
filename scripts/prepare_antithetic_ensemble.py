"""Prepare one matched antithetic ensemble after both native noninferiority tests."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_bounded_retry_native import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/antithetic_ensemble_protocol.json';recipe=json.loads(protocol.read_text());path=root/recipe['native_run']/'manifest.json';m=json.loads(path.read_text());result=analyze(m)
    if not result.get('antithetic_qualified'):raise ValueError('Antithetic native criteria failed')
    head=next(h for h in m['config']['heads'] if h['name']=='compact500_antithetic');basepath=root/recipe['baseline_run']/'manifest.json';base=json.loads(basepath.read_text());c={k:v for k,v in base['config'].items() if not k.startswith('parent_')}
    if base['status']!='complete' or base['config']['name']!='compact500' or (c['checkpoint'],c['checkpoint_sha256'])!=(head['checkpoint'],head['checkpoint_sha256']) or c['native_manifest_sha256']!=m['config']['prior_retry_manifest_sha256'] or not c['compact_condition']:raise ValueError('Unmatched compact control')
    for key in ('checkpoint','training_manifest'):
        if sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
    c.update(name='compact500_antithetic',latent_noise_scheme='antithetic',native_manifest=str(path),native_manifest_sha256=sha(path),protocol=str(protocol),protocol_sha256=sha(protocol))
    for key,value in dict(positive_parent_manifest=basepath,positive_parent_predictions=basepath.parent/'predictions.h5',positive_parent_scores=root/recipe['baseline_scores']).items():c[key]=str(value);c[key+'_sha256']=sha(value)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(c['name'])

if __name__=='__main__':main()
