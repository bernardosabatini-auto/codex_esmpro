"""Bound sources for the frozen conditional-decoder resolution diagnostic."""
import json
from pathlib import Path
from prepare_overfit import sha


def audit(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed diagnostic source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text());source=json.loads(Path(c['source_manifest']).read_text());gc=source['config'];d=json.loads(Path(c['source_report']).read_text())
    if (spec!=c['spec'] or source['status']!='complete' or d['status']!='complete' or d['profile_only']
        or not d.get('fragment_inpainting') or not d['numerically_qualified'] or d['updates']!=2000
        or Path(c['source_manifest']).parent.name!=spec['source'] or d['manifest_sha256']!=sha(c['source_manifest'])
        or d['predictions_sha256']!=sha(c['source_predictions']) or source['checkpoint_sha256']!=sha(c['checkpoint'])
        or c['selected']!=gc['selected'] or len(c['selected'])!=32
        or any(c[k]!=gc[k] for k in ('fragments','decoder_checkpoint'))
        or spec['steps']!=[3,10] or spec['probe_times']!=[0,1/3,2/3,.9] or spec['samples']!=4):
        raise ValueError('Unbound frozen inpainting diagnostic')
    return spec,gc,source
