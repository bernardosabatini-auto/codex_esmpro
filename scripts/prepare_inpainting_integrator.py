import argparse,json
from pathlib import Path
from prepare_overfit import sha
from inpainting_integrator_core import audit


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/inpainting_integrator_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['source'];gc=json.loads((run/'manifest.json').read_text())['config']
    c=dict(spec=spec,selected=gc['selected'],allocation_minutes=10,work_cap_seconds=480,sources=[])
    for key,path in [('protocol',protocol),('source_manifest',run/'manifest.json'),('source_report',root/'reports'/(run.name+'.json')),('checkpoint',run/'checkpoint.pt'),('source_predictions',run/'predictions.h5'),('fragments',gc['fragments']),('decoder_checkpoint',gc['decoder_checkpoint'])]:
        path=Path(path).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('32 training proteins,3/10 steps, no model updates')


if __name__=='__main__':main()
