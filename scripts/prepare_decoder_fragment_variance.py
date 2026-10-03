import argparse
import json
from pathlib import Path
from decoder_fragment_variance_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/decoder_fragment_variance_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['baseline_generation'];bc=json.loads((run/'manifest.json').read_text())['config']
    c=dict(spec=spec,target_ids=bc['target_ids'],selected=bc['selected'],allocation_minutes=10,work_cap_seconds=480,sources=[])
    def bind(path):
        path=Path(path).resolve();c['sources'].append(dict(path=str(path),sha256=sha(path)));return str(path)
    for key,path in [('protocol',protocol),('baseline_manifest',run/'manifest.json'),('baseline_report',root/'reports'/(run.name+'.json')),('baseline_predictions',run/'predictions.h5'),('fragments',bc['fragments']),('decoder_checkpoint',bc['decoder_checkpoint'])]:c[key]=bind(path)
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('32 proteins;640 generated-latent decodes,160 native decodes,32 single/batch controls')


if __name__=='__main__':main()
