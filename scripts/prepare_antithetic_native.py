"""Freeze an antithetic sampler comparison at the already qualified500 weights."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_bounded_retry_native import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];path=root/'runs/bounded_retry_native_49843256/manifest.json';m=json.loads(path.read_text());result=analyze(m)
    if not all(result['summaries'][h]['quality_passed'] for h in ('original','compact500')):raise ValueError('Missing qualified controls')
    c=dict(m['config']);heads=[dict(h,latent_noise_scheme='iid') for h in c['heads'] if h['name'] in ('original','compact500')];candidate=dict(heads[1],name='compact500_antithetic',latent_noise_scheme='antithetic');heads.append(candidate)
    protocol=root/'configs/antithetic_native_protocol.json'
    if [h['name'] for h in heads]!=json.loads(protocol.read_text())['heads']:raise ValueError('Wrong declared heads')
    for head in heads:
        for key in ('checkpoint','training_manifest','raw_manifest'):
            if head.get(key) and sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),prior_retry_manifest=str(path),prior_retry_manifest_sha256=sha(path),work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(heads=[h['name'] for h in heads],same_candidate_weights=heads[1]['checkpoint_sha256']==heads[2]['checkpoint_sha256'])))

if __name__=='__main__':main()
