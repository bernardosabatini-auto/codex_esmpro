"""Bind a fixed32-protein calibration without inspecting generation outcomes."""
import argparse
import json
from pathlib import Path
import h5py

from fragment_preference_calibration import native_inventory, select_sources, audit_generation
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_preference_calibration_protocol.json'
    spec=json.loads(protocol.read_text());parent=root/'runs'/spec['parent'];m=json.loads((parent/'manifest.json').read_text())
    corpus=root/spec['corpus'];c=dict(arm='parent6000',spec=spec,sources=[],native_sources=[])
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in c['sources']:c['sources'].append(row)
        return str(path)
    for key,path in [('protocol',protocol),('model_manifest',parent/'manifest.json'),
                     ('model_report',root/'reports'/(parent.name+'.json')),('checkpoint',parent/'ema_2000.ckpt'),
                     ('historical_predictions',parent/'evaluation_2000.h5'),('historical_fragments',m['config']['fragments']),
                     ('decoder_checkpoint',m['config']['decoder_checkpoint']),('data_manifest',corpus/'manifest.json'),
                     ('data_report',corpus/'report.json'),('fragments',corpus/'fragments.h5'),
                     ('excluded_feedback_manifest',root/'runs/fragment_feedback_50080056/manifest.json'),
                     ('generation_profile_report',root/'reports/extra_fragment_validation_50118888.json'),
                     ('generation_profile_manifest',root/'runs/extra_fragment_validation_50118888/manifest.json')]:
        c[key]=bind(path)
    for name in spec['native_source_runs']:
        run=root/'runs'/name;sm=json.loads((run/'manifest.json').read_text())
        c['native_sources'].append({key:bind(path) for key,path in
            [('manifest',run/'manifest.json'),('report',root/'reports'/(name+'.json')),
             ('refolded',run/'refolded.h5'),('predictions',sm['config']['predictions'])]})
    inventory=native_inventory(c)
    excluded=json.loads(Path(c['excluded_feedback_manifest']).read_text())['config']['selected_training_ids']
    c['selected']=select_sources(spec,inventory,excluded);c['target_ids']=sorted(r['id'] for r in c['selected'])
    with h5py.File(c['fragments']) as f:
        c['control_ids']=[min(i for i in m['config']['evaluation_train_ids']
                             if (int(f['train/'+i].attrs['length'])+127)//128*128==b) for b in (128,256,384,512)]
    audit_generation(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Bound32 training proteins,128generations; original32native budgets reused.')


if __name__=='__main__':main()
