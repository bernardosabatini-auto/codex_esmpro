import argparse,json
from pathlib import Path
import h5py
from prepare_overfit import sha
from extra_fragment_validation_core import audit_config


def main():
    p=argparse.ArgumentParser();p.add_argument('--arm',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_extra_validation_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['parents'][a.arm];data=root/'runs'/spec['encoded_cohort'];m=json.loads((run/'manifest.json').read_text());c=dict(arm=a.arm,spec=spec,control_ids=m['config']['control_ids'],sources=[])
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in c['sources']:c['sources'].append(row)
        return str(path)
    for key,path in [('protocol',protocol),('model_manifest',run/'manifest.json'),('model_report',root/'reports'/(run.name+'.json')),('checkpoint',run/'ema_2000.ckpt'),('historical_predictions',run/'evaluation_2000.h5'),('historical_fragments',Path(m['config']['fragments'])),('decoder_checkpoint',Path(m['config']['decoder_checkpoint'])),('data_manifest',data/'manifest.json'),('data_report',root/'reports'/(data.name+'.json')),('fragments',data/'fragments.h5')]:c[key]=bind(path)
    with h5py.File(c['fragments']) as f:c['target_ids']=sorted(f['development'])
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
