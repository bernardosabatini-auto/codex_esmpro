"""Bind two final models and all16families before drawing a new noise seed."""
import argparse,json
from pathlib import Path
import h5py
from fragment_validation_core import audit_config
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_validation_protocol.json';spec=json.loads(protocol.read_text());c=dict(spec=spec,models={},sources=[])
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in c['sources']:c['sources'].append(row)
        return str(path)
    c['protocol']=bind(protocol);c['discovery_report']=bind(root/'reports'/(spec['discovery_report']+'.json'))
    for arm,runname in spec['parents'].items():
        run=root/'runs'/runname;m=json.loads((run/'manifest.json').read_text());c['models'][arm]={k:bind(path) for k,path in [('manifest',run/'manifest.json'),('report',root/'reports'/(runname+'.json')),('checkpoint',run/'ema_2000.ckpt'),('historical_predictions',run/'evaluation_2000.h5')]}
    for key,source in [('fragments','fragments'),('decoder_checkpoint','decoder_checkpoint'),('native_predictions','initial_predictions')]:c[key]=bind(m['config'][source])
    with h5py.File(c['fragments']) as f:c['target_ids']=sorted(f['development'])
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
