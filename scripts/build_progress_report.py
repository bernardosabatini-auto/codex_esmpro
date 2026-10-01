"""Generate a compact aggregate-only HTML report from explicit project artifacts."""
import datetime
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    path = ROOT/relative
    return json.loads(path.read_text()) if path.exists() else None


def current_round():
    execution=read('runs/autonomous_20261001.json')
    if not execution:return []
    esc=html.escape
    lines=['<h2>Autonomous recovery and selection round</h2>',
        f'<p>Authorized window: {esc(execution["started"])} through {esc(execution["deadline"])}. At most eight project GPUs pending or running; only registered project jobs are inspected. Earlier-layer ESM allocation remains zero.</p>']
    registry=read('runs/jobs.json');state=read('runs/watch/state.json') or {};beat=read('runs/watch/heartbeat.json') or {}
    lines.append(f'<p>Scheduler snapshot from the project watcher: {esc(beat.get("checked_at","unavailable"))}; watcher status {esc(beat.get("status","unknown"))}. Pending requests are not running GPU computation.</p>')
    lines.append('<table><tr><th>Job</th><th>Question</th><th>Task states at snapshot</th></tr>')
    for job in (registry or {}).get('jobs',[]):
        if job.get('submitted','') < execution['started']:continue
        tasks=state.get('jobs',{}).get(job['id'],{}).get('tasks',{})
        values=', '.join(f'{name}: {row["state"]}' for name,row in tasks.items()) or job['state']
        lines.append(f'<tr><td>{esc(job["id"])}</td><td>{esc(job["purpose"])}</td><td>{esc(values)}</td></tr>')
    lines.append('</table><p>The recovery screens change optimizer beta2, loss reduction, or training-pool size separately. Checkpoint diagnostics compare the training-selected epoch-22 EMA and final raw weights with final EMA. The efficiency profile measures all-block versus pair-only activation recomputation before any training-policy change.</p>')
    d=read('reports/consensus_final_ema.json')
    if d:
        s=d['pairs']['tm_fixed_reference']['sample_mean'];ci=s['ci95']
        lines.append(f'<p><strong>Reference-free selection screen:</strong> choosing the most mutually consistent of three predictions raised TM from {s["ours"]:.5f} to {s["theirs"]:.5f}; change {s["theirs_minus_ours"]:+.5f}, 95% cluster interval [{ci[0]:+.5f}, {ci[1]:+.5f}]. lDDT and aggregate geometry also improved. Choices were frozen before reading native scores. This falls below the +0.01 practical accuracy target and requires two new inference-noise replications.</p>')
    for path in sorted((ROOT/'reports').glob('recovery_*.json')):
        d=read(str(path.relative_to(ROOT)))
        for row in d.get('runs',{}).values():
            tm=row['paired']['tm_fixed_reference'];delta=row['vs_untouched']['tm_fixed_reference']['theirs_minus_ours']
            lines.append(f'<p>Recovery {esc(row["task"]["name"])}: TM {tm["theirs"]:.5f}, change versus control {tm["theirs_minus_ours"]:+.5f}, versus untouched {delta:+.5f}; screen passed: {row["recovery_screen_passed"]}.</p>')
        for failure in d.get('failures',[]):lines.append(f'<p>Recovery result unavailable: {esc(failure["error"])}.</p>')
    return lines


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    esc = html.escape
    lines = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>ESM–ProteinAE experiment results</title><style>body{max-width:1050px;margin:40px auto;padding:0 24px;font:16px/1.5 system-ui;color:#17212b}table{border-collapse:collapse;width:100%}td,th{text-align:left;border-bottom:1px solid #ccc;padding:8px}small{color:#52616e}a{color:#2059a1}</style>',
        '<h1>ESM → ProteinAE: current evidence</h1>',f'<small>Generated from recorded artifacts at {stamp}. This is a saved snapshot.</small>',
        '<p>Earlier-layer ESM work is deferred, with no GPU allocation. Current work tests the causes of continued-training regression, saved-checkpoint choice, reference-free sample selection and GPU efficiency.</p>',
        *current_round(),
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
    online=read('runs/online_49470256/manifest.json')
    if online and online['status']=='complete':
        s=read('runs/online_49470256/scores.json')['summaries']['steps25_cfg2']
        lines.append(f'<tr><td>Pair, fresh final-layer ESMC, strict FP32</td><td>{s["mean_tm_fixed_reference"]:.5f}</td><td>{s["mean_ca_lddt"]:.5f}</td><td>{s["predictions"]}/1878</td></tr>')
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
        if d and d.get('decision'):
            lines.append(f'<p><strong>{name}:</strong> {esc(d["decision"])} Complete accuracy coverage was not achieved for all seeds.</p>');continue
        if not d or d['status']!='complete':
            lines.append(f'<p>{name}: full paired analysis pending.</p>');continue
        s=d['mean_across_training_seeds']['tm_fixed_reference'];ci=s['ci95']
        lines.append(f'<p><strong>{name}:</strong> matched mean TM change {s["theirs_minus_ours"]:+.5f}, 95% sequence-cluster interval [{ci[0]:+.5f}, {ci[1]:+.5f}]. Development gate passed: {d["development_gate_passed"]}.</p>')
    geometry=read('reports/pilot_49461023.json');quality=read('reports/quality_49466461.json')
    if geometry and geometry.get('decision') and quality and quality['status']=='complete' and not quality['development_gate_passed']:
        lines.append('<p><strong>Decision:</strong> neither recipe meets the accuracy promotion rule. Retain the untouched checkpoint. Do not scale these recipes or distil an unimproved latent teacher.</p>')
        lines.append('<p><strong>Next accuracy question:</strong> why does latent-only continued training regress from 0.56824 to 0.56576 mean TM? First audit the resume policy and training distribution, then isolate those changes in a bounded control experiment before adding another objective. The 1,024-protein pilot does not establish a general accuracy ceiling.</p>')
    lines += ['<h2>Independent test</h2>']
    holdout=read('runs/holdout_expanded_20260930/holdout.json')
    if holdout:
        lines.append(f'<p>Expanded score-blind curation: {esc(holdout["status"])}. Eligible targets recovered: {holdout.get("selected_count",0)}; minimum 32. Original September and January–September screens yielded three and 11 targets respectively. Releases since January 2024 are screened with the same sequence exclusion, residue correspondence and 90% observed-CA coverage requirements.</p>')
        if holdout['status']=='complete':
            lines.append(f'<p>Final manifest SHA256: <code>{esc(holdout["locked_sha256"])}</code>. No model scores have been computed on this set. It remains unused because neither development recipe passed promotion.</p>')
            counts=holdout['stratum_counts']
            lines.append(f'<p>Length coverage: {counts["True"]} chains at ≤256 residues and {counts["False"]} at 257–512. The long-chain stratum is too small for a strong accuracy claim.</p>')
        if holdout.get('error'):lines.append(f'<p>{esc(holdout["error"])}</p>')
    lines += ['<p>Independence from the frozen ESMC, ProteinAE and comparator pretraining sets is unknown.</p>',
        '<h2>Hardware and scope</h2><p>The validated training batches are 128/64/32/16 proteins at padded lengths 128/256/384/512. Training uses an FP16 head with checked parameter gradients and a strict FP32 decoder. Actual training measured approximately 96–97% SM activity but only 41% instruction issue where full counters were available; peak reserved memory was approximately 84–99 GiB. SM activity and instruction issue are not percent of peak FLOPs.</p>',
        '<p>External-model inference measured 81.1% SM activity during collection and 74.6% over the capture. Its timing includes sequence conditioning; the cached pair-head timing excludes ESMC. No end-to-end speed ratio is claimed.</p>',
        '<h2>Evidence and reproducibility</h2><ul>']
    cost=read('runs/accuracy_execution_cost.json')
    if cost:
        lines.insert(-1,f'<p>The prior objective/confidence/online-comparison round used {cost["gpu_hours"]:.3f} H200 GPU-hours across {cost["tasks"]} registered tasks, including failed jobs and setup time. Peak simultaneous allocation: {cost["peak_allocated_gpus"]} GPUs. This excludes the new autonomous recovery round.</p>')
    perf=read('reports/online_49470256.json')
    if perf and perf['status']=='complete':
        h=perf['hardware']['collection_mean_percent']
        lines.insert(-1,f'<p>Measured complete-pipeline throughput: {perf["proteins_per_second"]:.2f} proteins/s, three structures each, with {perf["peak_reserved_gib"]:.1f} GiB reserved. Computation: {h["SMs Active [Throughput %]"]:.1f}% SM activity and {h["SM Issue [Throughput %]"]:.1f}% instruction issue. Development accuracy/geometry noninferiority passed: {perf.get("development_noninferiority_passed", "pending")}.</p>')
    for filename in ('comparison_49414524.md','external_49461971.md','external_strata_49461971.md','geometry_49453471.md','training_data_v1.md','canonical_frames_v1.md','training_profile_49459162.md','pilot_49461023.md','quality_49466461.md','online_49468214.md','online_49470256.md','holdout_expanded_20260930.md','recovery_data_16384.md','training_state_audit.md','consensus_final_ema.md'):
        if (ROOT/'reports'/filename).exists():lines.append(f'<li><a href="{filename}">{filename}</a></li>')
    lines += ['</ul><p>Code and aggregate reports are synchronized to GitHub. Datasets, weights, target manifests, predictions and profiler traces remain local and ignored by Git.</p></html>']
    (ROOT/'reports/progress.html').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
