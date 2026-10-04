"""Prepare two exactly matched isolated-fragment endpoint profiles or runs."""
import argparse
import json
from pathlib import Path
from repaint_student_training_core import audit,load_pairs
from teacher_coordinates_profile_core import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=['native_matched','repaint_positive'],required=True)
    p.add_argument('--profile',action='store_true');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--labels',type=Path,required=True);p.add_argument('--profile-comparison',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/repaint_student_pilot_protocol.json';spec=json.loads(protocol.read_text())
    lp=a.labels.resolve()/'manifest.json';labels=json.loads(lp.read_text())
    bp=root/'runs/extra_fragment_validation_50188437/manifest.json';baseline=json.loads(bp.read_text());bc=baseline['config']
    c=dict(repaint_student_training=True,arm=a.arm,spec=spec,profile_only=a.profile,updates=40 if a.profile else 400,sources=[],
           training_ids=[r['label_id'] for r in labels['rows']],control_ids=[next(r['id'] for r in bc['selected'] if r['bucket']==b) for b in (128,256,384,512)],
           sampling_seed=bc['spec']['seed'],allocation_minutes=10,work_cap_seconds=480)
    def bind(path):
        path=Path(path).resolve();c['sources'].append(dict(path=str(path),sha256=sha(path)));return str(path)
    for key,path in [('protocol',protocol),('labels_manifest',lp),('baseline_manifest',bp),('baseline_report',root/'reports/extra_fragment_validation_50188437.json'),('initial_predictions',bp.parent/'predictions.h5')]:c[key]=bind(path)
    for key in ('checkpoint','decoder_checkpoint','fragments'):c[key]=bind(labels[key])
    if not a.profile:
        if a.profile_comparison is None:raise ValueError('Paired qualified profiles required')
        c['profile_comparison']=bind(a.profile_comparison);report=json.loads(a.profile_comparison.read_text())
        c['allocation_minutes']=report['recommended_full_minutes'];c['work_cap_seconds']=60*c['allocation_minutes']-120
    spec,labels=audit(c);load_pairs(c,audited=(spec,labels))
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print(c['arm'],c['updates'],len(c['training_ids']),c['allocation_minutes'])


if __name__=='__main__':main()
