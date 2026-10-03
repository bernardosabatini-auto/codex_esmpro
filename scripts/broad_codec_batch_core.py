import json
from pathlib import Path
import h5py,numpy as np
from generate_isolated_motif import canonical_fragment
from prepare_overfit import sha


def audit(c):
    for key in ('protocol','parent_manifest','parent_report','parent_fragments','historical_fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed codec batch source')
    spec=json.loads(Path(c['protocol']).read_text());pm=json.loads(Path(c['parent_manifest']).read_text());pd=json.loads(Path(c['parent_report']).read_text())
    if spec!=c['spec'] or Path(c['parent_manifest']).parent.name!=spec['parent'] or pm['status']!='complete' or pd['status']!='complete' or not pd['data_gate_passed'] or pd['manifest_sha256']!=c['parent_manifest_sha256'] or pd['fragments_sha256']!=c['parent_fragments_sha256'] or pm['config']['decoder_checkpoint']!=c['decoder_checkpoint'] or pm['config']['historical_fragments']!=c['historical_fragments']:raise ValueError('Unqualified batch parent')
    return pm


def items(c):
    pm=audit(c);result=[]
    with h5py.File(c['parent_fragments']) as src,h5py.File(c['historical_fragments']) as old:
        for ident in pm['config']['control_ids']:
            q=old['development/'+ident+'/conditions/f30_center'];result.append(dict(key='historical/'+ident,target_id=ident,kind='historical',backbone=q['fragment'][:],expected_latent=q['latent'][:],stream='historical_unused:0'))
        for ident,g in src['train'].items():
            bb=g['reference_backbone'][:];result.append(dict(key='full/'+ident,target_id=ident,kind='full',backbone=bb,reference_latent=g['reference_z'][:],expected_encoded=g['encoded_z'][:],expected_backbone=g['roundtrip'][:],stream='broad_full:0'))
            for name,q in g['conditions'].items():result.append(dict(key='fragment/'+ident+'/'+name,target_id=ident,kind='fragment',backbone=q['fragment'][:],expected_latent=q['latent'][:],expected_backbone=q['roundtrip'][:],stream='broad_fragment:'+name))
            for position,start in [('left',0),('center',(len(bb)-20)//2),('right',len(bb)-20)]:
                name='c20_'+position;fragment,_=canonical_fragment(bb[start:start+20].astype(np.float64));result.append(dict(key='new/'+ident+'/'+name,target_id=ident,kind='new',backbone=fragment,stream='broad_fragment:'+name))
    if len(result)!=836:raise ValueError('Changed codec profile inventory')
    return result
