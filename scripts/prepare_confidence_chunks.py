"""Freeze eight saved-output controls before profiling smaller confidence batches."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];base=root/'runs/expansion_data_49805944/manifest.json';m=json.loads(base.read_text());c=m['config']
    if m['status']!='complete' or not m['resource_gate_passed']:raise ValueError('profile incomplete')
    targets=[dict(r,labels=r['raw_labels'],labels_sha256=r['raw_labels_sha256']) for r in c['controls']]
    for b in (128,256,384,512):
        r=max((r for r in c['targets'] if r['bucket']==b),key=lambda r:(r['length'],r['id']));targets.append(dict(r,labels=str(base.parent/'labels.h5'),labels_sha256=m['labels_sha256']))
    protocol=root/'configs/confidence_chunks_protocol.json';config=dict(protocol=str(protocol),protocol_sha256=sha(protocol),base_profile=str(base),base_profile_sha256=sha(base),seed=c['seed'],teacher_artifacts=c['teacher_artifacts'],targets=targets)
    a.output.write_text(json.dumps(config,indent=2)+'\n');print(json.dumps(dict(targets=[r['id'] for r in targets],lengths=[r['length'] for r in targets])))


if __name__=='__main__':main()
