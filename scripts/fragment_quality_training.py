"""Bind condition-quality training to the fixed, matched training-only selection."""
from collections import Counter
import json
from pathlib import Path
from prepare_overfit import sha


def selection_for_config(c):
    if not c.get('condition_selection'):return None
    protocol=json.loads(Path(c['broad_corpus_protocol']).read_text())
    if not protocol.get('condition_quality_study'):raise ValueError('Undeclared condition selection')
    root=Path(c['broad_corpus_protocol']).parent.parent
    path=Path(c['condition_selection'])
    if path!=(root/protocol['selection_report']).resolve() or sha(path)!=c['condition_selection_sha256'] or sha(path)!=protocol['selection_report_sha256']:
        raise ValueError('Changed condition selection')
    d=json.loads(path.read_text())
    if d['status']!='complete' or not d['qualified'] or sha(d['protocol'])!=d['protocol_sha256'] or sha(d['quality_report'])!=d['quality_report_sha256']:
        raise ValueError('Unqualified condition-quality inventory')
    plan=json.loads(Path(d['protocol']).read_text());quality=json.loads(Path(d['quality_report']).read_text())
    if quality['sources'].get(c['fragments'])!=c['fragments_sha256']:raise ValueError('Wrong selected fragment corpus')
    arm=protocol['arms'][c['extension_arm']]['selection_arm']
    if arm not in ('control','quality'):raise ValueError('Wrong quality-selection arm')
    lookup={(r['id'],r['condition']):r for r in quality['records']}
    targets={r['id']:r for r in json.loads(Path(c['data_manifest']).read_text())['config']['training_targets']}
    if len(d['entries'])!=plan['proteins'] or len({r['id'] for r in d['entries']})!=plan['proteins'] or {r['id'] for r in d['entries']}!=set(targets):
        raise ValueError('Changed selected protein inventory')
    gains=[]
    for bucket in (128,256,384,512):
        rows=[r for r in d['entries'] if r['bucket']==bucket]
        if Counter(r['control'] for r in rows)!=Counter(r['quality'] for r in rows):raise ValueError('Unmatched condition placement')
        for r in rows:
            if targets[r['id']]['bucket']!=bucket:raise ValueError('Changed target length bucket')
            for route in ('control','quality'):
                q=lookup[r['id'],r[route]]
                if q['motif_length']!=20 or q['mean_plddt']!=r[route+'_confidence']:raise ValueError('Changed selected condition quality')
        gain=sum(r['quality_confidence']-r['control_confidence'] for r in rows)/len(rows)
        if gain<plan['minimum_bucket_confidence_gain']:raise ValueError('Failed bucket quality separation')
        gains.extend(r['quality_confidence']-r['control_confidence'] for r in rows)
    if sum(gains)/len(gains)<plan['minimum_overall_confidence_gain']:raise ValueError('Failed overall quality separation')
    return {r['id']:r[arm] for r in d['entries']}


def compare_quality_traces(manifests):
    if len(manifests)!=2:raise ValueError('Two matched arms required')
    rows=list(manifests.values());a,b=rows
    if len(a['training'])!=len(b['training']):raise ValueError('Unequal training exposure')
    fields=('step','length','batch','ids','learning_rate_factor','self_conditioned',
            'noise_sha256','time_sha256','drop_sha256','rng_sha256','global_rng_sha256')
    selections=[selection_for_config(m['config']) for m in rows]
    if any(s is None for s in selections):raise ValueError('Missing condition selection')
    for left,right in zip(a['training'],b['training']):
        if any(left[k]!=right[k] for k in fields):raise ValueError('Unmatched protein/RNG/LR draws')
        for r,s in zip((left,right),selections):
            if r['conditions']!=[s[i] for i in r['ids']]:raise ValueError('Wrong declared condition draws')
    return len(a['training'])
