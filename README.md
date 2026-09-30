# ESM → ProteinAE restart

Start with [the critical review and staged plan](reports/review.html), then the
[H200 profiling summary](reports/h200_profile.md) and
[batch precision diagnosis](reports/batch_precision.md), plus the
[proposed experiment settings](configs/first_experiments.json).

The completed 626-target run is summarized in
[the frozen-head comparison](reports/comparison_49414524.md).

This is a minimal research core, extracted from the original project with
[symbol-level provenance](PROVENANCE.json). It retains both flow architectures
and the differentiable decoder adapter. It adds explicit loss/sampling settings,
per-target RNG streams, strict HDF5 reads, strict paired statistics, and a cached
embedding prediction command. The user authorized autonomous H200 scheduling on
2026-09-29, with a maximum of eight GPUs across this project's running and pending
requests. Only inspect/manage job IDs recorded in `runs/jobs.json`; other agents
are working under the same account.

The original project, all datasets, pretrained weights, and the patched
ProteinAE checkout remain external. The old gate scripts are never imported.
The default loss reduction is per protein; use `FlowConfig(reduction="residue")`
for the old residue-weighted objective. Treat that choice as an experiment.

## Run the CPU checks

The inherited environment has the dependencies; it was read without modification.
From this directory:

```bash
export CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export PYTHONPATH="$PWD/src"
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
SOURCE=/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae

"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" scripts/audit_existing.py --source "$SOURCE" --output reports/existing_audit.json
"$PYTHON" scripts/check_legacy_parity.py --source "$SOURCE" --output reports/legacy_parity.json
```

`pyproject.toml` describes core dependencies for a separate environment. Full
ProteinAE decoding additionally needs the dependencies of the existing checkout.
The tested environment versions are recorded in `reports/verification.json`.

## Prediction entry point

`scripts/predict.py --help` describes inference from a cached-embedding HDF5 and
an explicit target-ID file. It loads EMA weights from a legacy full checkpoint,
or a weights file with its JSON sidecar, and emits per-sample latent and backbone
NPZ files plus a run manifest. Output directories must be new. CPU is the default;
CUDA requires `--device cuda --allow-gpu`; project authorization is already recorded.

For trusted local full checkpoints, `--trusted-legacy-pickle` may be necessary
because old training checkpoints contain Python optimizer/RNG state. This is a
serialization option, not GPU authorization. Decoder loading also assumes a
trusted local ProteinAE checkpoint.

The prediction command uses cached embeddings. Its timing is labeled accordingly
and must not be presented as end-to-end sequence folding. Frozen ESMC extraction
and a matched end-to-end benchmark are future work in the plan.

## Scope and limits

- Tested: thirteen CPU contract tests; exact forward parity of small pair and pair-free
  models against isolated original definitions; a real pretrained ProteinAE
  decoder on one validation target; the full 626-target artifact/data audit.
- H200 job 49346371 completed 50 throughput/memory configurations of the actual
  legacy heads and decoder. All eight real-weight cache equivalence checks gave
  exactly identical coordinates. Nsight counters are analyzed separately from
  nvidia-smi GPU busy time in `reports/h200_profile.json`.
- New-model accuracy has not been tested. No improved structure predictor has
  been trained. The scheduled comparison concerns existing frozen checkpoints.
- `flow_loss` supports training, but this restart does not carry over the old
  distributed trainer, RAM caches, monkey patches, or scheduling machinery.
- `usalign_fixed_tm` requires an external US-align executable. A pinned local
  build has passed rigid-transform, correspondence-permutation, and mirror
  controls. The CPU comparison scorer can report optimized, fixed-correspondence
  TM-score using `--usalign PATH`; the binary and its sources remain untracked.
- The current HDF5 files lack original residue maps. New builds must preserve
  them. Reading old records strictly cannot reconstruct missing provenance.
- No generator/design pipeline is copied. That branch needs separate controls,
  novelty searches, and motif evaluation before more investment.

## Batched comparison

`scripts/collect_comparison.py` consumes the fixed 626-target manifest and the
profile-derived batch sizes in `configs/comparison626.json`. It checks real-weight
batch/padding equivalence before collecting 10/25/50-step, guidance 1/2 predictions
with three reproducible samples each. GPU inference and asynchronous disk writes
overlap; optional CPU scoring runs concurrently on allocated host cores. All latents and backbone
coordinates are retained in HDF5. No best-of-three selection is performed.

`scripts/score_comparison.py --run RUN_DIRECTORY --workers 4` scores a completed
collection on CPUs. It checks exact target/sample coverage and reports CA lDDT,
RMSD, and geometry diagnostics. `tm_after_kabsch` is explicitly a diagnostic and
must not be reported as optimized TM-score. Add `--usalign PATH` to measure
optimized fixed-correspondence TM-score separately. ESMC timing remains required
for a full comparison with sequence folding.

The first comparison attempt (49349478) stopped at the real-weight batching
controls before collecting the sweep. One control differed by 0.43–0.64 Å RMSD
between padded batch and unpadded single inference. The source of this numerical
difference was traced primarily to BF16 flow computation. The selected flow
policy now uses strict IEEE FP32 for both flow and decoder. BF16, FP16, and
high-precision float32 matmul each failed at least one numerical shape control.
Strict FP32 passed the focused short/long diagnoses, at roughly three times
the flow cost. The comparison also validates actual production batch shapes
before the full sweep. See the numerical diagnosis above for scope and results.

The current account has no usable CPU-only submission route: the lab account has
a zero submission limit, and the Kempner account is not allowed on the CPU
partitions tested. The comparison therefore overlaps one CPU scoring process
with GPU inference, using CPU cores already included in its allocation. It
records the final scoring wait separately. The standard wrapper requests two
H200s via two independent tasks, each limited to 90 minutes; GPU count remains
bounded by the project-wide limit of eight.

## Completion monitoring

`scripts/install_watcher.py` installs the project-specific user systemd timer
`esm-proae-reboot-watch.timer`. It runs `scripts/watch_jobs.py` once per minute
on the installation host, survives terminal disconnection, and resumes after a
host restart when the user systemd manager is available. User lingering is already
enabled on the current host; the installer does not change that policy.

The watcher queries only exact registered IDs in `runs/jobs.json`. It reports
completion, failure, timeout, missing scheduler records, and analysis errors in
`runs/watch/events.jsonl`; `heartbeat.json` records its health. Notifications target
only the tmux pane/session captured at installation. It never types into tmux,
submits/cancels jobs, starts agents, or sends email. A tmux alert does not wake an
idle Codex conversation. During active experiments, continue work/checks through
completion instead of ending the task at submission.

For a two-task comparison, register `"completion_action": "summarize_comparison"`.
Once both scheduler tasks succeed, the watcher automatically checks exact score
coverage and provenance, calculates paired target-bootstrap intervals, joins
Nsight counters to inference batches, and writes `reports/comparison_JOB.md`.
Raw JSON remains local. Failed analysis is retried with bounded backoff. Completed
analyses are recorded and not repeated each minute. New experiment types need an
explicit supported follow-up action before submission.

```bash
"$PYTHON" scripts/install_watcher.py
systemctl --user status esm-proae-reboot-watch.timer
cat runs/watch/heartbeat.json runs/watch/state.json
```

The timer uses no GPU. Each check has a five-minute maximum, a one-core CPU limit,
and a 1 GiB memory limit; idle checks exit immediately. To uninstall monitoring,
disable only this project's timer with
`systemctl --user disable --now esm-proae-reboot-watch.timer`.

## Repository synchronization

The code repository is <https://github.com/bernardosabatini-auto/codex_esmpro>.
Datasets, weights, embeddings, predictions, logs, raw result JSON, target manifests,
and profiler traces are excluded by `.gitignore`. Written reviews and summary
reports are versioned; their underlying measurements remain local. References
to `reports/*.json`, `runs/`, and generated comparison configuration therefore
refer to local artifacts, not files distributed through GitHub.

After running and summarizing profiling, regenerate the local comparison inputs:

```bash
"$PYTHON" scripts/prepare_comparison.py --source "$SOURCE" \
  --profile reports/h200_profile.json --output configs/comparison626.json
```
