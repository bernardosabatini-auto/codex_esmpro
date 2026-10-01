"""Native quality/validity screen before spending GPU time on sampler ensembles."""
import hashlib,json
from pathlib import Path
import numpy as np
from summarize_distillation_campaign import comparison


def native_screen(manifest, step, sampling_steps):
    c=manifest['config'];raw=Path(c['selection']).read_bytes();selection=json.loads(raw)
    if hashlib.sha256(raw).hexdigest()!=c['selection_sha256']:raise ValueError('changed tuning selection')
    ids=sorted(r['id'] for r in selection['tuning'])
    if len(ids)!=64 or len({r['family'] for r in selection['tuning']})!=64:raise ValueError('expected 64 tuning families')
    values=[]
    for update,n in ((0,25),(step,sampling_steps)):
        rows=[r for r in manifest['scores'] if r['step']==update and r['sampling_steps']==n]
        if len(rows)!=192 or {r['target_id'] for r in rows}!=set(ids) or any(sorted(r['sample'] for r in rows if r['target_id']==i)!=[0,1,2] for i in ids):raise ValueError('native evaluation incomplete')
        values.append({k:[float(np.mean([r[k] for r in rows if r['target_id']==i])) for i in ids] for k in ('ca_lddt','coarse_valid')})
    metrics={key:comparison(values[1][key],values[0][key]) for key in values[0]}
    return dict(passed=bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01),step=step,sampling_steps=sampling_steps,metrics=metrics)
