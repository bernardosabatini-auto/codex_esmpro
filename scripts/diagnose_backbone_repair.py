"""Fixed training-only feasibility screen; never loads native/test references."""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
import h5py
import numpy as np
import torch
from latentfold.backbone_repair import repair_backbone, acceptance
from latentfold.ensemble_metrics import backbone_geometry


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol', type=Path, default=Path('configs/backbone_repair_protocol.json'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); protocol = json.loads(a.protocol.read_text()); torch.set_num_threads(1)
    result = dict(status='running', protocol=dict(path=str(a.protocol), sha256=sha(a.protocol)), code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), sources=[], timing='CPU single thread; includes initial geometry screening and attempted repairs for all32 samples; excludes reading cached H5, startup, and independent post-checks')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    # Initialize PyTorch optimizer imports on synthetic data, before timed inference.
    synthetic = np.zeros((12, 4, 3), dtype=np.float32)
    synthetic[:, :, 0] = np.arange(12)[:, None]*3.8+np.array([-1.23, 0, 1.23, 1.23])
    synthetic[5, :, 0] += .4
    start = time.perf_counter(); repair_backbone(synthetic, protocol['repair'])
    result['startup_seconds'] = time.perf_counter()-start
    for source in protocol['training_sources']:
        record = dict(path=source, sha256=sha(source), targets=[], initial_invalid=0, repaired=0, initially_valid_changed=0, accepted_constraint_violations=0)
        with h5py.File(source) as f:
            if len(f) != protocol['targets_per_source']: raise ValueError('training target count changed')
            for target in sorted(f):
                bb = f[target]['cfg1']['backbone'][:]
                if len(bb) != protocol['samples_per_target']: raise ValueError('sample count changed')
                start = time.perf_counter()
                before = {k: np.concatenate([backbone_geometry(bb[i:i+4])[k] for i in range(0, len(bb), 4)]) for k in ('coarse_valid',)}
                out = bb.copy(); diagnostics = []
                for i in np.flatnonzero(~before['coarse_valid']):
                    out[i], diag = repair_backbone(bb[i], protocol['repair']); diagnostics.append(dict(sample=int(i), **diag))
                elapsed = time.perf_counter()-start
                unchanged = np.array_equal(out[before['coarse_valid']], bb[before['coarse_valid']])
                after = np.concatenate([backbone_geometry(out[i:i+4])['coarse_valid'] for i in range(0, len(bb), 4)])
                repaired = int((after & ~before['coarse_valid']).sum())
                violations = sum(not acceptance(bb[d['sample']], out[d['sample']], protocol['repair'])[0] for d in diagnostics if d['status'] == 'repaired')
                invalid = int((~before['coarse_valid']).sum())
                record['initial_invalid'] += invalid; record['repaired'] += repaired
                record['initially_valid_changed'] += int(not unchanged); record['accepted_constraint_violations'] += violations
                record['targets'].append(dict(target_id=target, initial_invalid=invalid, repaired=repaired, seconds=elapsed, diagnostics=diagnostics))
        seconds = [r['seconds'] for r in record['targets']]
        record['mean_seconds_per_32_samples'] = float(np.mean(seconds)); record['max_seconds_per_32_samples'] = max(seconds)
        record['repaired_fraction'] = record['repaired']/record['initial_invalid'] if record['initial_invalid'] else None
        gate = protocol['feasibility']
        record['feasible'] = record['repaired_fraction'] is not None and record['repaired_fraction'] >= gate['minimum_repaired_fraction_each_seed'] and record['mean_seconds_per_32_samples'] <= gate['max_mean_seconds_per_32_samples'] and record['max_seconds_per_32_samples'] <= gate['max_seconds_per_32_samples'] and not record['initially_valid_changed'] and not record['accepted_constraint_violations']
        result['sources'].append(record)
        print(json.dumps({k:v for k,v in record.items() if k!='targets'}), flush=True)
        a.output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    result['status'] = 'complete'; result['feasible_both_seeds'] = all(s['feasible'] for s in result['sources'])
    a.output.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    lines = ['# Bounded backbone repair: training feasibility', '', 'Fixed122 training targets ×32 samples at two balanced2000 seeds. No reference structures in repair. All initially valid predictions remain unchanged; failed repairs return the original. No sample deletion or resampling. Coarse validity is not a physical certificate.', '', '| Source | Invalid | Repaired | Fraction | Mean seconds/32 | Maximum seconds/32 | Feasible |', '|---|---:|---:|---:|---:|---:|---|']
    for s in result['sources']:
        lines.append(f"| {s['path']} | {s['initial_invalid']} | {s['repaired']} | {s['repaired_fraction']:.4f} | {s['mean_seconds_per_32_samples']:.4f} | {s['max_seconds_per_32_samples']:.4f} | {s['feasible']} |")
    lines += ['', f"Both-seed feasibility: **{result['feasible_both_seeds']}**. Frozen requirement: at least50% of invalid samples repaired in each seed, mean added CPU time≤0.25s and maximum≤2s per32 samples, no invariant violations. Timing includes screening all samples and repair attempts, excludes cached H5 reading, startup, and independent checks.", '', f"Protocol `{a.protocol}`, SHA256 `{result['protocol']['sha256']}`. Code commit `{result['code_commit']}`. Adam is coordinatewise and this prototype does not claim arbitrary-rotation equivariance; coordinate inputs retain the existing canonical frame. No native or external qualification is inferred."]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__': main()
