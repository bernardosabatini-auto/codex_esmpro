"""Bind final native-anchor models to the unchanged32-source diagnostic assay."""
import argparse
import copy
import json
from pathlib import Path
from prepare_overfit import sha


def check_recipe(spec, baseline):
    changed={'historical_seed','work_cap_seconds','scope','decision','resources'}
    if any(spec[k]!=v for k,v in baseline.items() if k not in changed):
        raise ValueError('Changed baseline sampler, targets, teacher or design budget')
    if (spec.get('native_anchor_model_validation') is not True
            or spec.get('historical_condition')!='c20_center'
            or spec.get('historical_prefix')!='conditioned'
            or spec.get('historical_seed')!=2026100413
            or spec.get('work_cap_seconds')!=480):
        raise ValueError('Wrong endpoint historical controls')


def audit_generation(c):
    from fragment_preference_calibration import audit_generation as audit_baseline
    for row in c['sources']:
        if sha(row['path'])!=row['sha256']:raise ValueError('Changed model-validation source')
    spec=json.loads(Path(c['protocol']).read_text())
    base=json.loads(Path(c['baseline_manifest']).read_text())
    bd=json.loads(Path(c['baseline_report']).read_text());bc=base['config']
    if bc['spec'].get('native_anchor_model_validation'):raise ValueError('Recursive validation baseline')
    audit_baseline(bc)
    check_recipe(spec,bc['spec'])
    if (spec!=c['spec'] or Path(c['baseline_manifest']).parent.name!=spec['baseline_generation']
            or base['status']!='complete' or bd['status']!='complete'
            or bd['manifest_sha256']!=sha(c['baseline_manifest'])
            or bd['predictions_sha256']!=sha(Path(c['baseline_manifest']).parent/'predictions.h5')):
        raise ValueError('Unqualified original generation')
    for key in ('target_ids','selected','native_sources','fragments','data_manifest','data_report'):
        if c[key]!=bc[key]:raise ValueError('Changed diagnostic inventory: '+key)
    m=json.loads(Path(c['model_manifest']).read_text());d=json.loads(Path(c['model_report']).read_text());mc=m['config']
    paired=json.loads(Path(c['matched_training_report']).read_text())
    run=Path(c['model_manifest']).parent
    if (m['status']!='complete' or d['status']!='complete' or not d['numerically_qualified']
            or mc['profile_only'] or mc['updates']!=400 or d['updates']!=400
            or d['manifest_sha256']!=sha(c['model_manifest'])
            or c['checkpoint']!=str(run/'ema_400.ckpt') or d['checkpoint_sha256']!=sha(c['checkpoint'])
            or c['historical_predictions']!=str(run/'evaluation_400.h5')
            or c['arm']!=mc['arm'] or c['arm'] not in ('positive','contrastive')
            or mc['checkpoint']!=bc['checkpoint'] or c['decoder_checkpoint']!=mc['decoder_checkpoint']
            or c['historical_fragments']!=mc['fragments'] or c['control_ids']!=mc['control_ids']
            or mc['sampling_seed']!=spec['historical_seed'] or m['peak_reserved_GiB']>75
            or paired['status']!='complete' or not paired['qualified'] or paired['profile_only']
            or paired['matched_updates']!=400 or paired['protocol_sha256']!=sha(mc['protocol'])
            or Path(mc['protocol']).name!=Path(spec['training_protocol']).name
            or not any(r['manifest_sha256']==sha(c['model_manifest']) and r['report_sha256']==sha(c['model_report']) for r in paired['sources'])):
        raise ValueError('Unqualified final400 model or matched inference profile')
    labels=json.loads(Path(mc['labels_manifest']).read_text())
    label_generation=json.loads(Path(labels['generation_manifest']).read_text())
    if set(c['target_ids']) & set(label_generation['config']['target_ids']):
        raise ValueError('Diagnostic targets overlap native-anchor source cohort')
    if set(c['control_ids']) & set(c['target_ids']):raise ValueError('Historical control overlaps diagnostic')
    return spec


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.run.resolve()
    protocol=root/'configs/native_anchor_model_validation_protocol.json';spec=json.loads(protocol.read_text())
    baseline=root/'runs'/spec['baseline_generation'];base=json.loads((baseline/'manifest.json').read_text())
    m=json.loads((run/'manifest.json').read_text());mc=m['config'];c=copy.deepcopy(base['config'])
    c.update(arm=mc['arm'],spec=spec,control_ids=mc['control_ids'])
    def bind(path):
        path=Path(path).resolve();row=dict(path=str(path),sha256=sha(path))
        if row not in c['sources']:c['sources'].append(row)
        return str(path)
    for key,path in [('protocol',protocol),('baseline_manifest',baseline/'manifest.json'),
                     ('baseline_report',root/'reports'/(baseline.name+'.json')),
                     ('model_manifest',run/'manifest.json'),('model_report',root/'reports'/(run.name+'.json')),
                     ('checkpoint',run/'ema_400.ckpt'),('historical_predictions',run/'evaluation_400.h5'),
                     ('historical_fragments',mc['fragments']),('decoder_checkpoint',mc['decoder_checkpoint']),
                     ('matched_training_report',root/'reports/native_anchor_training_full_20261003.json')]:c[key]=bind(path)
    labels=json.loads(Path(mc['labels_manifest']).read_text());bind(mc['labels_manifest']);bind(labels['generation_manifest']);bind(mc['protocol'])
    audit_generation(c)
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print(c['arm'],len(c['target_ids']),'targets; full128-output refolding required')


if __name__=='__main__':main()
