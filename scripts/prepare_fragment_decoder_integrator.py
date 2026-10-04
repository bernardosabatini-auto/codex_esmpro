import argparse,json
from pathlib import Path
from fragment_decoder_integrator_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_decoder_integrator_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['source_run']
    gc=json.loads((run/'manifest.json').read_text())['config']
    c=dict(spec=spec,selected=gc['selected'],sources=[],allocation_minutes=spec['allocation_minutes'],work_cap_seconds=spec['work_cap_seconds'])
    for key,value in [('protocol',protocol),('source_manifest',run/'manifest.json'),('source_report',root/'reports'/(run.name+'.json')),('source_predictions',run/'predictions.h5'),('checkpoint',run/'checkpoint.pt'),('fragments',gc['fragments']),('decoder_checkpoint',gc['decoder_checkpoint'])]:
        path=Path(value).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('32proteins,4noises,512free outputs,1536oracle path predictions,oneRTX10minutes')


if __name__=='__main__':main()
