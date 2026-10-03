"""Bound isolated inputs for the additional experimental development cohort."""
import json
from pathlib import Path
import numpy as np
from generate_isolated_motif import canonical_fragment
from prepare_overfit import sha


def crop_condition(backbone,sequence):
    n=len(sequence);k=max(8,int(.3*n));start=(n-k)//2
    if backbone.shape!=(n,4,3):raise ValueError('Wrong complete reference shape')
    fragment,degenerate=canonical_fragment(backbone[start:start+k].astype(np.float64))
    return start,sequence[start:start+k],fragment,degenerate


def audit_config(c):
    for key in ('selection','backbones','decoder_checkpoint','historical_fragments','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed additional-fragment source '+key)
    selection=json.loads(Path(c['selection']).read_text());spec=json.loads(Path(c['protocol']).read_text())
    if c['spec']!=spec or selection['status']!='complete' or selection['counts']!={'short':32,'long':32} or selection['backbones_sha256']!=c['backbones_sha256'] or len(selection['selected'])!=64 or len({r['family'] for r in selection['selected']})!=64:raise ValueError('Unqualified additional cohort')
    for path,digest in selection['sources'].items():
        if sha(path)!=digest:raise ValueError('Changed selection provenance')
    if c['target_ids']!=sorted(r['target_id'] for r in selection['selected']) or len(c['control_ids'])!=4:raise ValueError('Changed encoding inventory')
    return selection
