import argparse,json
from pathlib import Path
from fragment_repaint_teacher_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_repaint_teacher_protocol.json';spec=json.loads(protocol.read_text())
    base=root/'runs'/spec['baseline_generation'];hist=root/'runs'/spec['historical_generation']
    bc=json.loads((base/'manifest.json').read_text())['config'];hc=json.loads((hist/'manifest.json').read_text())['config']
    c=dict(spec=spec,selected=bc['selected'],target_ids=bc['target_ids'],native_sources=bc['native_sources'],arm='oracle_repaint',
           allocation_minutes=15,work_cap_seconds=780,sources=[])
    pairs=[('protocol',protocol),('baseline_manifest',base/'manifest.json'),('baseline_report',root/'reports'/(base.name+'.json')),
           ('baseline_predictions',base/'predictions.h5'),('historical_manifest',hist/'manifest.json'),('historical_report',root/'reports'/(hist.name+'.json')),
           ('historical_predictions',hist/'predictions.h5'),('historical_selection',hc['selection']),('historical_parent_predictions',hc['parent_predictions']),
           ('checkpoint',hc['checkpoint']),('decoder_checkpoint',bc['decoder_checkpoint']),('fragments',bc['fragments'])]
    for key,value in pairs:
        path=Path(value).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Oracle teacher:128 outputs,16 historical controls;oneRTX15minutes')


if __name__=='__main__':main()
