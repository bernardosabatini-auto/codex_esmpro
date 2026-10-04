"""Bound provenance and complete inventory for decoder integration diagnosis."""
import json
from pathlib import Path
from fragment_decoder_fm_core import audit as audit_training
from prepare_overfit import sha


def audit(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']: raise ValueError('Changed integrator source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text())
    m=json.loads(Path(c['source_manifest']).read_text()); d=json.loads(Path(c['source_report']).read_text()); gc=m['config']
    audit_training(gc)
    if (spec!=c['spec'] or Path(c['source_manifest']).parent.name!=spec['source_run']
            or m['status']!='complete' or d['status']!='complete' or not d.get('fragment_decoder_fm')
            or d['profile_only'] or not d['numerically_qualified'] or d['qualified']
            or d['manifest_sha256']!=sha(c['source_manifest']) or d['checkpoint_sha256']!=sha(c['checkpoint'])
            or d['predictions_sha256']!=sha(c['source_predictions']) or m['checkpoint_sha256']!=sha(c['checkpoint'])
            or d['updates']!=2000 or d['controls']!=192 or len(gc['selected'])!=32
            or c['selected']!=gc['selected'] or c['fragments']!=gc['fragments'] or c['decoder_checkpoint']!=gc['decoder_checkpoint']
            or spec['steps']!=[3,10] or spec['samples']!=4 or spec['seed']!=gc['spec']['sampling_seed']
            or c['allocation_minutes']!=10 or c['work_cap_seconds']!=480):
        raise ValueError('Changed frozen decoder integration diagnostic')
    return spec,gc,m
