"""Pure validation helpers for the frozen alternating benchmark."""
import hashlib
import json
import math
import numpy as np

ORDER = [['reference','candidate'], ['candidate','reference'], ['reference','candidate']]
VARIANTS = {'reference':dict(embedding='fp32',head='fp32',steps=25,reuse=False),
            'candidate':dict(embedding='fp16',head='fp16_mlp',steps=20,reuse=True)}


def fingerprint(identities, arrays):
    digest = hashlib.sha256(json.dumps(identities).encode())
    for array in arrays:
        value = np.asarray(array)
        digest.update(str((value.shape,str(value.dtype))).encode())
        digest.update(value.tobytes())
    return digest.hexdigest()


def timing_result(manifest):
    if manifest['order'] != ORDER or manifest['variants'] != VARIANTS:
        raise ValueError('changed alternating protocol')
    passes = manifest['passes']
    if [(p['repeat'],p['variant']) for p in passes] != [(i,n) for i,order in enumerate(ORDER) for n in order]:
        raise ValueError('incomplete or reordered passes')
    ids = set(manifest['config']['target_ids'])
    first = {}
    repeats = [{}, {}, {}]
    identical = True
    for p in passes:
        batches = p['batches']
        if p['status'] != 'complete' or set(p['choices'])!=ids or any(type(k) is not int or not 0<=k<3 for k in p['choices'].values()):
            raise ValueError('invalid timed choice coverage')
        if not batches or sum(b['batch'] for b in batches)!=3*len(ids) or sum(b['proteins'] for b in batches)!=len(ids):
            raise ValueError('incomplete timing coverage')
        if len(p['fingerprints'])!=len(batches) or any(len(s)!=64 for s in p['fingerprints']):
            raise ValueError('missing prediction fingerprints')
        if any(not math.isfinite(b['seconds']) or b['seconds']<=0 or not 0<=b['selection_seconds']<=b['seconds'] or b['batch']!=3*b['proteins'] for b in batches):
            raise ValueError('invalid batch timing')
        shape = [(b['length'],b['batch']) for b in batches]
        signature = (p['fingerprints'],p['choices'],shape)
        first.setdefault(p['variant'],signature)
        match = signature == first[p['variant']]
        if p['identical_to_first'] != match:
            raise ValueError('repeat identity claim disagrees with fingerprints')
        identical &= match
        seconds = sum(b['seconds'] for b in batches)
        repeats[p['repeat']][p['variant']] = dict(seconds=seconds,proteins_per_second=len(ids)/seconds,
            selection_seconds=sum(b['selection_seconds'] for b in batches),
            peak_reserved_gib=max(b['peak_reserved_bytes'] for b in batches)/2**30)
    if first['reference'][2] != first['candidate'][2]:
        raise ValueError('unequal reference/candidate batch shapes')
    for row in repeats:
        row['speedup'] = row['reference']['seconds']/row['candidate']['seconds']
    return dict(repeats=repeats, repeated_outputs_identical=identical,
        speed_gate_passed=identical and all(r['speedup']>=2 for r in repeats))


def selected_rows(rows, choices):
    groups = {}
    for row in rows:
        key = row['target_id'], row['sample']
        if key in groups:
            raise ValueError('duplicate native score')
        groups[key] = row
    if set(groups) != {(name,k) for name in choices for k in range(3)} or any(type(k) is not int or not 0<=k<3 for k in choices.values()):
        raise ValueError('invalid choice/score coverage')
    return [groups[name,k] for name,k in sorted(choices.items())]
