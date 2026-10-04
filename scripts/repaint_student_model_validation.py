"""Fixed32 generation for both endpoint arms, including label and other families."""
import argparse
import copy
import json
from pathlib import Path
from teacher_coordinates_profile_core import sha


def check_recipe(spec,base):
    changed={'historical_seed','work_cap_seconds','scope','decision','resources'}
    if any(spec.get(k)!=v for k,v in base.items() if k not in changed):raise ValueError('Changed sampler, sequence budget or panel')
    if (spec.get('repaint_student_model_validation') is not True or spec['historical_seed']!=base['seed']
            or spec['historical_condition']!='c20_center' or spec['historical_prefix']!='conditioned'
            or spec['work_cap_seconds']!=480):raise ValueError('Changed final-checkpoint controls')


def require_refold_eligibility(report):
    if report.get('status')!='complete' or report.get('controls')!=68 or len(report.get('records',[]))!=128:
        raise ValueError('Complete audited128-output generation required')
    raw=sum(r['raw_gate_passed'] for r in report['records']);valid=sum(r['coarse_valid'] for r in report['records'])
    if raw<9 or valid<45:raise ValueError('Student cannot meet the prespecified parent success counts')
    return dict(raw=raw,valid=valid,qualified=True)


def audit_generation(c):
    from fragment_preference_calibration import audit_generation as audit_baseline
    from repaint_student_training_core import audit as audit_training
    base=json.loads(Path(c['baseline_manifest']).read_text());bc=base['config']
    if bc['spec'].get('repaint_student_model_validation') or bc['arm']!='parent6000':raise ValueError('Recursive baseline')
    audit_baseline(bc);verified={r['path']:r['sha256'] for r in bc['sources']}
    for source in c['sources']:
        if source['path'] not in verified:verified[source['path']]=sha(source['path'])
        if verified[source['path']]!=source['sha256']:raise ValueError('Changed generation source')
    spec=json.loads(Path(c['protocol']).read_text());check_recipe(spec,bc['spec'])
    bd=json.loads(Path(c['baseline_report']).read_text())
    if (spec!=c['spec'] or base['status']!='complete' or bd['status']!='complete'
            or bd['manifest_sha256']!=sha(c['baseline_manifest'])
            or bd['predictions_sha256']!=sha(Path(c['baseline_manifest']).parent/'predictions.h5')):raise ValueError('Unqualified baseline')
    if any(c[k]!=bc[k] for k in ('target_ids','selected','native_sources','fragments','data_manifest','data_report')):
        raise ValueError('Changed32-source diagnostic population')
    m=json.loads(Path(c['model_manifest']).read_text());d=json.loads(Path(c['model_report']).read_text());mc=m['config'];_,labels=audit_training(mc)
    paired=json.loads(Path(c['matched_training_report']).read_text());run=Path(c['model_manifest']).parent
    if (m['status']!='complete' or d['status']!='complete' or not d['numerically_qualified']
            or mc['profile_only'] or mc['updates']!=400 or d['updates']!=400
            or d['manifest_sha256']!=sha(c['model_manifest']) or c['checkpoint']!=str(run/'ema_400.ckpt')
            or d['checkpoint_sha256']!=verified[c['checkpoint']] or c['historical_predictions']!=str(run/'evaluation_400.h5')
            or c['arm']!=mc['arm'] or c['arm'] not in ('native_matched','repaint_positive')
            or c['historical_fragments']!=mc['fragments'] or c['decoder_checkpoint']!=mc['decoder_checkpoint']
            or mc['checkpoint']!=bc['checkpoint'] or c['control_ids']!=mc['control_ids']
            or mc['sampling_seed']!=spec['historical_seed'] or m['peak_reserved_GiB']>75
            or paired['status']!='complete' or not paired['qualified'] or paired['profile_only'] or paired['matched_updates']!=400
            or paired['protocol_sha256']!=sha(mc['protocol']) or paired['labels_manifest_sha256']!=sha(mc['labels_manifest'])
            or Path(mc['protocol']).name!=Path(spec['training_protocol']).name):raise ValueError('Unqualified final400 endpoint')
    for path in (c['model_manifest'],c['model_report']):
        if not any(s['path']==path and s['sha256']==sha(path) for s in paired['sources']):raise ValueError('Unbound matched endpoint')
    trained=sorted({r['target_id'] for r in labels['rows']})
    if c['label_target_ids']!=trained or len(trained)!=9 or not set(trained)<=set(c['target_ids']):raise ValueError('Changed selected-label subgroup')
    return spec


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.run.resolve();m=json.loads((run/'manifest.json').read_text());mc=m['config']
    protocol=root/'configs/repaint_student_model_validation_protocol.json';spec=json.loads(protocol.read_text())
    baseline=root/'runs/extra_fragment_validation_50188437';base=json.loads((baseline/'manifest.json').read_text());c=copy.deepcopy(base['config'])
    labels=json.loads(Path(mc['labels_manifest']).read_text());c.update(arm=mc['arm'],spec=spec,control_ids=mc['control_ids'],label_target_ids=sorted({r['target_id'] for r in labels['rows']}))
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in c['sources']:c['sources'].append(row)
        return str(path)
    for key,path in [('protocol',protocol),('baseline_manifest',baseline/'manifest.json'),('baseline_report',root/'reports/extra_fragment_validation_50188437.json'),
                     ('model_manifest',run/'manifest.json'),('model_report',root/'reports'/(run.name+'.json')),('checkpoint',run/'ema_400.ckpt'),
                     ('historical_predictions',run/'evaluation_400.h5'),('historical_fragments',mc['fragments']),('decoder_checkpoint',mc['decoder_checkpoint']),
                     ('matched_training_report',root/'reports/repaint_student_training_full_20261004.json')]:c[key]=bind(path)
    bind(mc['labels_manifest']);bind(mc['protocol']);audit_generation(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print(c['arm'],len(c['target_ids']),len(c['label_target_ids']))


if __name__=='__main__':main()
