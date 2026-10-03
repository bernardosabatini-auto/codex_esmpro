import argparse
import json
from pathlib import Path
from native_positive_coverage import audit_generation
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    selection=root/'runs/native_positive_coverage_selection_20261003.json';s=json.loads(selection.read_text());profile=root/'runs/extra_fragment_validation_50194966';pc=json.loads((profile/'manifest.json').read_text())['config']
    c=dict(native_positive_coverage=True,arm='native_latent',spec=s['spec'],target_ids=s['target_ids'],selected=s['selected'],sources=[],allocation_minutes=10,work_cap_seconds=480,historical_seed=pc['spec']['native_seed'],control_ids=[min(r['id'] for r in pc['selected'] if r['bucket']==b) for b in (128,256,384,512)])
    for key,path in [('selection',selection),('protocol',s['protocol']),('fragments',s['fragments']),('decoder_checkpoint',pc['decoder_checkpoint']),('profile_manifest',profile/'manifest.json'),('profile_report',root/'reports'/(profile.name+'.json')),('profile_predictions',profile/'predictions.h5')]:
        path=Path(path).resolve();c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    audit_generation(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Prepared128 native decodes,64repeat controls,4historical controls; oneRTX10minutes')


if __name__=='__main__':main()
