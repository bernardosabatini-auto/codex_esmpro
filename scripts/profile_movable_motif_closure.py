"""Unfiltered paired CPU mechanism test; no training or designability claim."""
import argparse
import json
import time
from pathlib import Path
import h5py
import numpy as np
from latentfold.movable_motif_closure import close_movable_motif
from latentfold.backbone_sterics import steric_audit
from latentfold.local_closure import geometry_audit
from fragment_junction_core import flank_bonds
from fragment_validation_core import raw_rows
from audit_inpainting_junctions import junctions
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha
from profile_gpu import atomic_json


def score(output, source, parent, item, slot, bucket, spec, pose_arm):
    start, length, width = item['start'], spec['motif_length'], spec['flank_width']
    stop = start + length
    # Original isolated fragment remains the target, regardless of optimized pose.
    raw = raw_rows(output[None], item['fragment'], start, item['arm'], item['id'], item['family'])[0]
    local = geometry_audit(output, parent, start, length, width)
    edges, junction = flank_bonds(output,start,length,width), junctions(output,start,length)
    movable = list(range(start-width,stop+width))
    far = np.ones(len(source),dtype=bool)
    far[movable] = False
    far_exact = np.array_equal(output[far],source[far])
    a, b = output[start:stop].reshape(-1,3), source[start:stop].reshape(-1,3)
    ac, bc = a-a.mean(0), b-b.mean(0)
    u, _, vh = np.linalg.svd(ac.T @ bc)
    q = u @ np.diag([1.,1.,np.linalg.det(u@vh)]) @ vh
    rigidity = float(np.sqrt(np.mean(np.sum((ac@q-bc)**2,axis=-1))))
    pair_error = float(np.max(np.abs(np.linalg.norm(a[:,None]-a[None,:],axis=-1)
                                    -np.linalg.norm(b[:,None]-b[None,:],axis=-1))))
    if not far_exact or rigidity > 1e-4 or pair_error > 1e-4:
        raise ValueError('Fixed far scaffold or rigid proper motif changed')
    if pose_arm == 'fixed_pose' and not np.array_equal(output[start:stop],source[start:stop]):
        raise ValueError('Fixed-pose motif moved')
    atom = steric_audit(output,movable)
    physical = bool(raw['raw_gate_passed'] and local['valid'] and edges['all_edges_valid'] and junction['valid'])
    return dict(raw, pose_arm=pose_arm, generation_slot=slot, bucket=bucket, local_geometry=local,
        hidden_flank_bonds=edges, junctions=junction, far_exact=bool(far_exact),
        motif_rigid_rmsd=rigidity, motif_pair_distance_max_error=pair_error,
        nonbonded=atom, refold_eligible_geometry=physical,
        steric_eligible=bool(physical and atom['pairs_below_threshold']==0))


def evaluate(root, protocol, output):
    tick = time.monotonic()
    spec = json.loads(protocol.read_text())
    if spec['arms'] != ['fixed_pose','free_pose'] or spec['cpu_seconds_cap'] != 1800:
        raise ValueError('Changed paired protocol')
    baseline = root/'reports/torsion_closure_full_20261004.json'
    d = json.loads(baseline.read_text())
    old_spec = json.loads((root/'configs/torsion_bridge_closure_protocol.json').read_text())
    source = Path(d['run'])/'predictions.h5'
    if (sha(baseline) != '18dced564834de25b4f33a7d85c870c490078265f666191ccd697fe68f8815bc'
            or d['status']!='complete' or d['profile_only'] or sha(source)!=d['predictions_sha256']
            or sha(Path(d['manifest_path']))!=d['manifest_sha256'] or d['spec']!=old_spec):
        raise ValueError('Bound complete original full assay required')
    selected = [next(r for r in d['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    ids = [r['id'] for r in selected]
    previous = json.loads((root/old_spec['source_report']).read_text())
    training = json.loads(Path(previous['manifest_path']).read_text())
    items = load_conditions(training['config']['fragments'],ids,'c20_center',cohort='train')
    output.mkdir(parents=True,exist_ok=False)
    snapshot = output/'source_snapshot'
    snapshot.mkdir()
    files = [protocol,Path(__file__),root/'configs/torsion_bridge_closure_protocol.json']
    files += [root/'src/latentfold'/name for name in ('movable_motif_closure.py','torsion_closure.py',
        'internal_bridge.py','backbone_sterics.py','local_closure.py')]
    files += [root/'scripts'/name for name in ('fragment_junction_core.py','fragment_validation_core.py',
        'audit_inpainting_junctions.py','extra_fragment_validation_core.py')]
    for file in files:
        (snapshot/file.name).write_bytes(file.read_bytes())
    m = dict(status='running',profile_only=True,spec=spec,selected=selected,
        protocol_sha256=sha(protocol),baseline_report=str(baseline),baseline_report_sha256=sha(baseline),
        baseline_predictions_sha256=sha(source),sources={str(f):sha(f) for f in files},
        records=[],controls=[],run=str(output.resolve()))
    atomic_json(output/'manifest.json',m)
    rng = np.random.default_rng(2026100901)
    deadline = tick + spec['cpu_seconds_cap']
    try:
        with h5py.File(source,'r',locking=False) as original,h5py.File(output/'predictions.h5','x',locking=False) as out:
            for row in selected:
                ident, bucket = row['id'],row['bucket']
                item = items[ident]
                for arm in ('generated_cond','native_cond'):
                    for slot in range(4):
                        key = arm+'/'+ident+'/'+str(slot)
                        g = original[key]
                        parent,before = g['parent'][:],g['source'][:]
                        for pose_arm in spec['arms']:
                            free = pose_arm=='free_pose'
                            result,stats = close_movable_motif(before,parent,item['start'],20,old_spec,
                                free_pose=free,deadline=deadline)
                            record = score(result,before,parent,dict(item,id=ident,arm=arm),slot,bucket,old_spec,pose_arm)
                            record['solver'] = stats
                            m['records'].append(record)
                            group = out.require_group(pose_arm+'/'+key)
                            for name,value in [('source',before),('parent',parent),('backbone',result)]:
                                group[name] = value
                            if slot==0:
                                noop,ns = close_movable_motif(parent,parent,item['start'],20,old_spec,free_pose=free,deadline=deadline)
                                repeat,_ = close_movable_motif(before,parent,item['start'],20,old_spec,free_pose=free,deadline=deadline)
                                q,_ = np.linalg.qr(rng.normal(size=(3,3)))
                                q[:,0] *= np.linalg.det(q)
                                shift = rng.normal(size=3)*10
                                moved,_ = close_movable_motif(before@q+shift,parent@q+shift,item['start'],20,old_spec,free_pose=free,deadline=deadline)
                                control = dict(arm=arm,pose_arm=pose_arm,target_id=ident,
                                    noop_exact=bool(np.array_equal(noop,parent)),noop_calls=ns['closure_calls'],
                                    repeat_exact=bool(np.array_equal(repeat,result)),
                                    pose_max_abs=float(np.max(np.abs(moved-result@q-shift))))
                                m['controls'].append(control)
                                if not control['noop_exact'] or control['noop_calls'] or not control['repeat_exact'] or control['pose_max_abs']>.005:
                                    raise ValueError('No-op/repeat/pose control failed')
                            out.flush()
                            atomic_json(output/'manifest.json',m)
                    print(ident,arm,'complete',flush=True)
        if len(m['records'])!=64 or len(m['controls'])!=16:
            raise ValueError('Incomplete paired profile')
        if any(sha(Path(file))!=digest for file,digest in m['sources'].items()) or sha(source)!=m['baseline_predictions_sha256']:
            raise ValueError('Inputs or scientific code changed during profile')
        summary=[]
        for pose_arm in spec['arms']:
            for arm in ('generated_cond','native_cond'):
                rr=[r for r in m['records'] if r['arm']==arm and r['pose_arm']==pose_arm]
                summary.append(dict(pose_arm=pose_arm,arm=arm,samples=len(rr),
                    physical=sum(r['refold_eligible_geometry'] for r in rr),
                    steric_eligible=sum(r['steric_eligible'] for r in rr),
                    overlap_cases=sum(r['nonbonded']['pairs_below_threshold']>0 for r in rr),
                    median_motif_displacement_rmsd=float(np.median([r['solver']['motif_displacement_rmsd'] for r in rr])),
                    median_torsion_rms_degrees=float(np.median([r['solver']['torsion_rms_degrees'] for r in rr]))))
        counts={(r['pose_arm'],r['arm']):r['steric_eligible'] for r in summary}
        qualified=(counts['free_pose','generated_cond']>=12
                   and counts['free_pose','generated_cond']>counts['fixed_pose','generated_cond']
                   and counts['free_pose','native_cond']==16)
        m.update(status='complete',summary=summary,qualified=qualified,seconds=time.monotonic()-tick,
                 predictions_sha256=sha(output/'predictions.h5'))
    except Exception as exc:
        m.update(status='failed',error=repr(exc),seconds=time.monotonic()-tick)
        atomic_json(output/'manifest.json',m)
        raise
    atomic_json(output/'manifest.json',m)
    return dict(m,manifest_sha256=sha(output/'manifest.json'))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--protocol',type=Path,default=Path('configs/movable_motif_closure_protocol.json'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    d=evaluate(Path(__file__).resolve().parents[1],a.protocol,a.output)
    atomic_json(a.report.with_suffix('.json'),d)
    lines=['# Paired movable-motif CPU profile','',
        'Constructive feasibility only; no learned-capacity or designability claim. All failed outputs retained.','',
        '| Pose | Context | Physical /16 | Physical and overlap-free /16 |',
        '|---|---|---:|---:|']
    for r in d['summary']:
        lines.append(f"| {r['pose_arm']} | {r['arm']} | {r['physical']} | {r['steric_eligible']} |")
    lines.extend(['',f"Qualified: {d['qualified']}. Runtime {d['seconds']:.2f} CPU seconds; no GPUs.",
        'Original isolated motif is the scoring target. Proper-pose, exact-repeat and no-op controls passed.',
        'All-atom rigid motif and bitwise fixed distant-scaffold checks passed for every output.',''])
    a.report.with_suffix('.md').write_text('\n'.join(lines))
    print(json.dumps({k:d[k] for k in ('status','qualified','seconds','summary')},indent=2))


if __name__=='__main__':main()
