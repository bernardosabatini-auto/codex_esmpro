"""Reference-free bounded retries on existing draws, with unchanged raw evidence."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha
from score_ensemble_states import state_definition
from summarize_student_extension import analyze as validate_extension
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from latentfold.teacher_states import paired_change


def select_draws(valid, outputs=32, attempts=4):
    valid = np.asarray(valid)
    if valid.dtype != np.bool_ or valid.shape != (outputs * attempts,):
        raise ValueError('Expected one boolean per complete stored draw')
    selected = np.arange(outputs)
    used = np.ones(outputs, dtype=int)
    for k in range(outputs):
        for a in range(attempts):
            index = k + outputs * a
            used[k] = a + 1
            if valid[index]:
                selected[k] = index
                break
    return selected, used


def metrics(indices, valid, quality, assigned):
    hits = set(assigned[indices].tolist()) - {-1}
    return dict(valid_fraction=float(valid[indices].mean()),
                oracle_ca_lddt=float(quality[indices].mean()),
                coverage=len(hits) / 2, both_states=float(len(hits) == 2))


def analyze_run(run, name):
    manifest = run / 'manifest.json'
    m = json.loads(manifest.read_text())
    if m['status'] != 'complete' or m['config']['name'] != name:
        raise ValueError('Wrong or incomplete source run')
    verified = validate_extension(m, run / 'predictions.h5')
    report = Path('reports') / (run.name + '.json')
    published = json.loads(report.read_text())
    if published['manifest_sha256'] != sha(manifest) or published['rows'] != verified['rows'] or published['definitions'] != verified['definitions']:
        raise ValueError('Raw extension no longer matches published evidence')
    prior = {r['target_id']: r for r in verified['rows']}
    panel = {r['query_id']: r for r in json.loads(Path(m['config']['panel']).read_text())['development']}
    rows = []
    with h5py.File(run / 'predictions.h5') as h:
        for ident in sorted(h):
            bb = h[ident]['backbone'][:]
            valid = np.concatenate([backbone_geometry(bb[k:k+32])['coarse_valid'] for k in range(0,128,32)])
            # Selection sees geometry only, before calculating reference scores.
            selected, used = select_draws(valid)
            pos, refs, i, j, features, labels = state_definition(panel[ident])
            if len(set(labels)) != 2:
                raise ValueError('Expected frozen two-state family')
            ca = bb[:,pos,1]
            quality = np.array([[ca_metrics(x,y)['ca_lddt'] for y in refs] for x in ca]).max(1)
            f = np.linalg.norm(ca[:,i] - ca[:,j], axis=-1)
            errors = np.sqrt(np.mean((f[:,None] - features[None])**2, axis=-1))
            nearest = errors.argmin(1)
            good = (errors[np.arange(128),nearest] <= 2.) & (quality >= .8) & valid
            assigned = np.where(good, np.asarray(labels)[nearest], -1)
            raw = metrics(np.arange(32), valid, quality, assigned)
            retry = metrics(selected, valid, quality, assigned)
            expected = prior[ident]
            for key in ('valid_fraction','oracle_ca_lddt'):
                if not np.isclose(raw[key], expected[key]['32'], atol=1e-12, rtol=0):
                    raise ValueError('First32 score mismatch')
            if raw['coverage'] != expected['coverage']['2.0']['32']:
                raise ValueError('First32 coverage mismatch')
            rows.append(dict(target_id=ident, family=panel[ident]['family'], raw=raw, retry=retry,
                             raw_validity=valid.tolist(), raw_oracle_ca_lddt=quality.tolist(),
                             raw_state_assignments=assigned.tolist(), selected_indices=selected.tolist(),
                             attempts_per_slot=used.tolist(), initially_invalid=int((~valid[:32]).sum()),
                             unresolved=int((~valid[selected]).sum())))
    families = {r['target_id']: r['family'] for r in rows}
    if len(rows) != 16 or len(set(families.values())) != 16:
        raise ValueError('Incomplete independent families')
    effects = {k: paired_change({r['target_id']:r['retry'][k] for r in rows},
                               {r['target_id']:r['raw'][k] for r in rows}, families=families)
               for k in rows[0]['raw']}
    initial = sum(r['initially_invalid'] for r in rows)
    unresolved = sum(r['unresolved'] for r in rows)
    total_attempts = sum(sum(r['attempts_per_slot']) for r in rows)
    feasible = (initial > 0 and (initial-unresolved)/initial >= .5
                and effects['coverage']['difference'] >= 0
                and effects['oracle_ca_lddt']['ci95'][0] > -.005)
    return dict(name=name, rows=rows, effects=effects, initially_invalid=initial, unresolved=unresolved,
                recovered=initial-unresolved, attempted_draws=total_attempts,
                attempts_per_output=total_attempts/512, historical_generated_draws=2048,
                feasibility_passed=feasible, definitions=verified['definitions'],
                sources={str(p):sha(p) for p in (manifest,run/'predictions.h5',report)})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol', type=Path, default=Path('configs/bounded_retry_diagnostic_protocol.json'))
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args(); protocol=json.loads(a.protocol.read_text())
    if (protocol['outputs'],protocol['max_attempts_per_output'],protocol['families']) != (32,4,16):
        raise ValueError('Protocol changed')
    arms={name:analyze_run(Path(path),name) for name,path in protocol['sources'].items()}
    if set(arms) != {'original','compact500'} or arms['original']['definitions'] != arms['compact500']['definitions']:
        raise ValueError('Unmatched pipelines')
    families={r['target_id']:r['family'] for r in arms['original']['rows']}
    if families != {r['target_id']:r['family'] for r in arms['compact500']['rows']}:
        raise ValueError('Mismatched family mapping')
    comparisons={mode:{key:paired_change({r['target_id']:r[mode][key] for r in arms['compact500']['rows']},
                                       {r['target_id']:r[mode][key] for r in arms['original']['rows']},families=families)
                       for key in ('coverage','both_states','valid_fraction','oracle_ca_lddt')}
                 for mode in ('raw','retry')}
    d=dict(status='complete',protocol_sha256=sha(a.protocol),arms=arms,comparisons=comparisons,
           feasibility_passed=all(x['feasibility_passed'] for x in arms.values()))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Bounded geometry retry feasibility','','CPU reuse of all16 frozen two-state development families. Four attempts per32 output slots, first coarse-valid draw only; exhausted slots return their original draw. Selection uses no reference scores. All128 historical draws and all failures remain in the raw record.','','| Pipeline | Initially invalid | Recovered | Still invalid | Attempted draws/output | Feasible |','|---|---:|---:|---:|---:|---|']
    for name,r in arms.items():
        lines.append(f"| {name} | {r['initially_invalid']}/512 | {r['recovered']} | {r['unresolved']} | {r['attempts_per_output']:.5f} | {r['feasibility_passed']} |")
    for name,r in arms.items():
        lines+=['',f'## {name} selected32 versus raw32','']
        for key,e in r['effects'].items():
            lines.append(f"- {key}: {e['reference']:.5f} → {e['candidate']:.5f}; change {e['difference']:+.5f}, paired-family95% interval {e['ci95']}.")
    lines+=['','## Matched compact500 minus original','']
    for mode,values in comparisons.items():
        for key,e in values.items():
            lines.append(f"- {mode} {key}: {e['difference']:+.5f}, paired-family95% interval {e['ci95']}.")
    lines+=['',f"Declared feasibility criterion: {d['feasibility_passed']}.",
            '', 'Attempted draws are a simulation cost proxy, not measured latency. Both source jobs already generated2048 draws. No runtime, memory or independent-generalization claim. Raw model gates are unchanged; this separately defined retry pipeline needs its own matched native and external evaluation before promotion. State coverage cannot decrease here because initially valid draws are retained; unchanged coverage is not evidence of new modes.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:{q:v[q] for q in ('initially_invalid','recovered','unresolved','attempts_per_output','feasibility_passed')} for k,v in arms.items()},indent=2))


if __name__=='__main__':main()
