"""Generate a compact aggregate-only HTML report from explicit project artifacts."""
import datetime
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    path = ROOT/relative
    return json.loads(path.read_text()) if path.exists() else None


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    esc = html.escape
    lines = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>ESM–ProteinAE experiment results</title><style>body{max-width:1050px;margin:40px auto;padding:0 24px;font:16px/1.5 system-ui;color:#17212b}table{border-collapse:collapse;width:100%}td,th{text-align:left;border-bottom:1px solid #ccc;padding:8px}small{color:#52616e}a{color:#2059a1}</style>',
        '<h1>ESM → ProteinAE: current evidence</h1>',f'<small>Generated from recorded artifacts at {stamp}. This is a saved snapshot.</small>',
        '<p>Earlier-layer ESM work is deferred, with no GPU allocation. Current tests change the training objective or source-confidence weights while retaining the same folding head.</p>',
        '<h2>Structure accuracy</h2><p>All 626 development proteins and three samples per protein; every sample retained. Fixed residue correspondence, optimized TM-score and CA lDDT. These are reused development data.</p>',
        '<table><tr><th>Model</th><th>Mean TM</th><th>CA lDDT</th><th>Coverage</th></tr>']
    baseline = read('reports/comparison_49414524.json')
    if baseline:
        for name, model in baseline['models'].items():
            s=model['scores']['steps25_cfg2']
            lines.append(f'<tr><td>Untouched {esc(name)}</td><td>{s["mean_tm_fixed_reference"]:.5f}</td><td>{s["mean_ca_lddt"]:.5f}</td><td>{s["predictions"]}/1878</td></tr>')
    external = read('runs/external_49461971/manifest.json')
    if external and external['status']=='complete':
        s=read('runs/external_49461971/scores.json')['summaries']['esmfold2_steps50_loops3']
        lines.append(f'<tr><td>ESMFold2-Fast</td><td>{s["mean_tm_fixed_reference"]:.5f}</td><td>{s["mean_ca_lddt"]:.5f}</td><td>{s["predictions"]}/1878</td></tr>')
    for pattern in ('pilot_49461023_*','quality_49466461_*'):
        for run in sorted((ROOT/'runs').glob(pattern)):
            if not run.is_dir(): continue
            t=read(str(run.relative_to(ROOT)/'training.json'));m=read(str(run.relative_to(ROOT)/'evaluation/manifest.json'))
            if not t: continue
            name=f'{t["task"]["arm"]}, seed {t["task"]["seed"]}'
            if m and m['status']=='complete':
                s=read(str(run.relative_to(ROOT)/'evaluation/scores.json'))['summaries']['steps25_cfg2']
                lines.append(f'<tr><td>{esc(name)}</td><td>{s["mean_tm_fixed_reference"]:.5f}</td><td>{s["mean_ca_lddt"]:.5f}</td><td>{s["predictions"]}/1878</td></tr>')
            else:
                lines.append(f'<tr><td>{esc(name)}</td><td colspan="3">Training {esc(t["status"])}, {t["steps"]}/500 updates; evaluation {esc(m["status"]) if m else "pending"}</td></tr>')
    lines += ['</table><h2>Paired decisions</h2>',
        '<p>Promotion requires a mean TM gain of at least 0.01, a positive sequence-cluster confidence bound, positive gains in all three training seeds, and no material lDDT or geometry regression. Independent final-test confirmation is required. A better training loss alone does not qualify.</p>']
    for name,relative in [('Geometry objective','reports/pilot_49461023.json'),('Confidence weighting','reports/quality_49466461.json')]:
        d=read(relative)
        if not d or d['status']!='complete':
            lines.append(f'<p>{name}: full paired analysis pending.</p>');continue
        s=d['mean_across_training_seeds']['tm_fixed_reference'];ci=s['ci95']
        lines.append(f'<p><strong>{name}:</strong> matched mean TM change {s["theirs_minus_ours"]:+.5f}, 95% sequence-cluster interval [{ci[0]:+.5f}, {ci[1]:+.5f}]. Development gate passed: {d["development_gate_passed"]}.</p>')
    lines += ['<h2>Independent test</h2>']
    holdout=read('runs/holdout_expanded_20260930/holdout.json')
    if holdout:
        lines.append(f'<p>Expanded score-blind curation: {esc(holdout["status"])}. Eligible targets recovered so far: {holdout.get("selected_count",0)}; minimum 32. Original September and January–September screens yielded three and 11 targets respectively. Releases since January 2024 are screened with the same sequence exclusion, residue correspondence and 90% observed-CA coverage requirements.</p>')
        if holdout.get('error'):lines.append(f'<p>{esc(holdout["error"])}</p>')
    lines += ['<p>Independence from the frozen ESMC, ProteinAE and comparator pretraining sets is unknown.</p>',
        '<h2>Hardware and scope</h2><p>The validated training batches are 128/64/32/16 proteins at padded lengths 128/256/384/512. Training uses an FP16 head with checked parameter gradients and a strict FP32 decoder. The final backward profile measured 90.1% SM activity during computation and 63.5% across the capture. Actual experiment counters are reported in the linked analyses. SM activity is not percent of peak FLOPs.</p>',
        '<p>External-model inference measured 81.1% SM activity during collection and 74.6% over the capture. Its timing includes sequence conditioning; the cached pair-head timing excludes ESMC. No end-to-end speed ratio is claimed.</p>',
        '<h2>Evidence and reproducibility</h2><ul>']
    for filename in ('comparison_49414524.md','external_49461971.md','external_strata_49461971.md','geometry_49453471.md','training_data_v1.md','canonical_frames_v1.md','training_profile_49459162.md','pilot_49461023.md','quality_49466461.md','holdout_expanded_20260930.md'):
        if (ROOT/'reports'/filename).exists():lines.append(f'<li><a href="{filename}">{filename}</a></li>')
    lines += ['</ul><p>Code and aggregate reports are synchronized to GitHub. Datasets, weights, target manifests, predictions and profiler traces remain local and ignored by Git.</p></html>']
    (ROOT/'reports/progress.html').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
