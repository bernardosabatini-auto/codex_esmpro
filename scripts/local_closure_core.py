import json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.local_closure import geometry_audit,topology
from audit_inpainting_junctions import junctions
from fragment_validation_core import raw_rows


ROTATION=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=np.float64)
OFFSET=np.array([11,13,-9],dtype=np.float64)


def make_config(root,profile,profile_report=None):
    protocol=root/'configs/fragment_local_closure_canonical_protocol.json';spec=json.loads(protocol.read_text())
    run=root/'runs/fragment_inpainting_training_50356015';m=json.loads((run/'manifest.json').read_text());old=m['config']
    selected=old['selected'];profile_ids=[next(r['id'] for r in selected if r['bucket']==b) for b in (128,256,384,512)]
    c=dict(profile_only=profile,spec=spec,profile_ids=profile_ids,selected=[r for r in selected if not profile or r['id'] in profile_ids],sources=[])
    def bind(k,p):
        p=Path(p).resolve();c[k]=str(p);c['sources'].append(dict(path=str(p),sha256=sha(p)))
    for k,p in [('protocol',protocol),('source_manifest',run/'manifest.json'),('source_predictions',run/'predictions.h5'),
                ('source_report',root/'reports/fragment_inpainting_training_50356015.json'),
                ('source_comparison',root/'reports/fragment_junction_comparison_20261004.json'),('fragments',old['fragments']),
                ('solver_code',root/'src/latentfold/local_closure.py'),('runner_code',root/'scripts/evaluate_local_closure.py'),
                ('core_code',root/'scripts/local_closure_core.py'),('audit_code',root/'scripts/summarize_local_closure.py')]:bind(k,p)
    if not profile:
        if profile_report is None:raise ValueError('Qualified CPU profile required')
        bind('profile_report',profile_report);r=json.loads(Path(profile_report).read_text())
        bind('profile_manifest',r['manifest_path']);bind('profile_predictions',Path(r['manifest_path']).parent/'predictions.h5')
    audit(c);return c


def audit(c):
    for r in c['sources']:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed closure source: '+r['path'])
    spec=json.loads(Path(c['protocol']).read_text());m=json.loads(Path(c['source_manifest']).read_text())
    d=json.loads(Path(c['source_report']).read_text());comparison=json.loads(Path(c['source_comparison']).read_text())
    if (spec!=c['spec'] or m['status']!='complete' or d['status']!='complete' or not d['numerically_qualified']
            or not d['junction_weighted'] or d['qualified'] or d['profile_only']
            or d['manifest_sha256']!=sha(c['source_manifest']) or d['predictions_sha256']!=sha(c['source_predictions'])
            or comparison['status']!='complete' or comparison['source_report_sha256']!=sha(c['source_report'])
            or comparison['refold_eligibility']!={'qualified':False,'connected_raw':1,'required':45}
            or c['fragments']!=m['config']['fragments']):raise ValueError('Unbound failed junction endpoint')
    selected=m['config']['selected'];ids=[next(r['id'] for r in selected if r['bucket']==b) for b in (128,256,384,512)]
    if c['profile_ids']!=ids or c['selected']!=[r for r in selected if not c['profile_only'] or r['id'] in ids]:
        raise ValueError('Changed fixed closure inventory')
    if not c['profile_only']:
        p=json.loads(Path(c['profile_report']).read_text())
        if (p['status']!='complete' or not p['profile_only'] or not p['qualified'] or p['protocol_sha256']!=sha(c['protocol'])
                or p['manifest_sha256']!=sha(c['profile_manifest']) or p['predictions_sha256']!=sha(c['profile_predictions'])):
            raise ValueError('Unqualified closure profile')
    return spec


def score(backbone,source,parent,item,arm,slot,bucket):
    local=geometry_audit(backbone,parent,item['start'],len(item['fragment']))
    junction=junctions(backbone,item['start'],len(item['fragment']))
    raw=raw_rows(backbone[None],item['fragment'],item['start'],arm,item['id'],item['family'])[0]
    fixed=np.ones(len(source),dtype=bool);fixed[topology(len(source),item['start'],len(item['fragment']),4)['residues']]=False
    if not np.array_equal(backbone[fixed],source[fixed]):raise ValueError('Changed fixed motif or far scaffold')
    return dict(raw,generation_slot=slot,bucket=bucket,local_geometry=local,junctions=junction,
        connected_raw=raw['raw_gate_passed'] and junction['valid'],
        qualified_raw=raw['raw_gate_passed'] and junction['valid'] and local['valid'],
        rms_atom_displacement=float(np.sqrt(np.mean((backbone-source)**2))),
        max_atom_displacement=float(np.linalg.norm(backbone-source,axis=-1).max()))
