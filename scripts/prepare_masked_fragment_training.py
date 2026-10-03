import argparse,json
from pathlib import Path
import h5py
from masked_fragment_training_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',action='store_true');p.add_argument('--profile-report',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/masked_fragment_flow_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['diagnostic'];pc=json.loads((run/'manifest.json').read_text())['config']
    c=dict(spec=spec,profile_only=a.profile,updates=spec['profile_updates'] if a.profile else spec['updates'],selected=pc['selected'],sources=[],allocation_minutes=20,work_cap_seconds=1080)
    def bind(path):
        path=Path(path).resolve();c['sources'].append(dict(path=str(path),sha256=sha(path)));return str(path)
    for key,path in [('protocol',protocol),('diagnostic_manifest',run/'manifest.json'),('diagnostic_report',root/'reports'/(run.name+'.json')),('diagnostic_predictions',run/'predictions.h5'),('fragments',pc['fragments']),('decoder_checkpoint',pc['decoder_checkpoint']),('baseline_predictions',pc['baseline_predictions'])]:c[key]=bind(path)
    with h5py.File(c['fragments']) as f:c['training_ids']=sorted(f['train'])
    if not a.profile:
        if a.profile_report is None:raise ValueError('Completed profile required')
        c['profile_report']=bind(a.profile_report);pr=json.loads(a.profile_report.read_text());c['allocation_minutes']=pr['recommended_full_minutes'];c['work_cap_seconds']=60*c['allocation_minutes']-120;c['profile_manifest']=bind(pr['manifest_path']);c['profile_checkpoint']=bind(str(Path(pr['manifest_path']).parent/'checkpoint.pt'))
    audit(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('profile' if a.profile else 'full',c['updates'],'updates;',len(c['training_ids']),'proteins;',c['allocation_minutes'],'minutes')


if __name__=='__main__':main()
