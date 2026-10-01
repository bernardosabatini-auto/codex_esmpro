# ESM → ProteinAE restart

Latest evidence and next experiments: [ensemble progress, October 1](reports/ensemble_progress_20261001.md).

See [the current results snapshot](reports/progress.html) for the active accuracy
experiments and their decisions.

Start with [the critical review and staged plan](reports/review.html), then the
[H200 profiling summary](reports/h200_profile.md) and
[batch precision diagnosis](reports/batch_precision.md), plus the
[proposed experiment settings](configs/first_experiments.json).

The completed 626-target run is summarized in
[the frozen-head comparison](reports/comparison_49414524.md).
The subsequent [hybrid precision experiment](reports/hybrid_49427699.md) validates
FP16 feed-forward layers for the pair model (1.59x cached-pipeline speedup) and
FP16 feed-forward layers plus attention projections for pair-free (2.62x).
Attention calculations, latent updates and the decoder remain FP32. The broader
policy failed the pair model's shape controls and is rejected. See
[the validated inference settings](configs/validated_inference.json); these are
development-set results and exclude ESMC extraction time.

The [corrected ESMFold2-Fast benchmark](reports/external_49626106.md) gives
TM 0.59983 versus 0.56824 for the unchanged pair head on 626 development proteins.
This replaces the earlier benchmark, whose HF port executed a disabled MSA
encoder with missing weights. The rerun confirms essentially the same accuracy
gap while fixing that invalid execution path; see the
[adapter audit](reports/teacher_adapter_audit_20261001.md).

The accuracy work now includes an actual continued-training loop, a
[structural-gradient diagnostic](reports/geometry_49453471.md),
[verified source-mapped training records](reports/training_data_v1.md), and
[backward capacity/precision validation](reports/training_profile_49459162.md).
Six independent single-H200 runs compare latent-only and bounded geometry
gradients over 500 updates and three paired seeds. A subsequent confidence
ablation reuses the three controls and changes only source-pLDDT residue weights.
Earlier-layer ESM work was reopened by the user on October 1. Neither continued
training nor the new losses are established accuracy improvements yet.

The [geometry pilot](reports/pilot_49461023.md) is now stopped: the two completed
geometry evaluations have TM changes of −0.00005 and −0.00004 relative to their
matched controls. The third geometry checkpoint failed the batch/padding
stability control. Its failed evaluation is preserved. The small positive local
lDDT changes do not satisfy the practical accuracy gate. Three confidence-weighted
runs were a separate ablation; they were not combined with the geometry loss.

The [confidence-weighting pilot](reports/quality_49466461.md) also completed:
mean paired TM change +0.00031, cluster interval [−0.00011, +0.00074]. It fails
the +0.01 improvement gate, including within the planned length strata. Neither
recipe is promoted or scaled. Keep the untouched checkpoint as the accuracy reference.

The latent-only control itself regressed from 0.56824 to 0.56576 mean TM.
It is continued training from EMA weights with a fresh optimizer, per-protein
loss reduction and a small, length-balanced subset, not an exact resumption of
the inherited training run. The loss comparisons are matched within this pilot;
they do not isolate why continued training regressed. The next accuracy experiment
should first separate the resume-policy and training-distribution effects before
adding another objective. These null pilots do not establish an accuracy ceiling.

The new [recovery protocol](configs/recovery_plan.json) isolates AdamW beta2,
residue-versus-protein loss reduction, and a verified 16,384-protein training
pool. Two saved-checkpoint comparisons and an activation-recomputation profile
run alongside those screens. The [saved-state audit](reports/training_state_audit.md)
validates all optimizer moments and parameter ordering; missing CUDA RNG state
prevents claiming an exact replay of the inherited run.

All three recovery screens completed without qualifying for replication:
[beta2 and loss reduction](reports/recovery_49523242.md) each changed TM by
about −0.00021 versus the matched trained control; the
[larger pool](reports/recovery_49526215.md) gained +0.00072 but remained
0.00117 below untouched final EMA. The next
[matched optimizer-history pair](configs/optimizer_state_plan.json) starts both
arms from identical raw weights and saved EMA, restoring AdamW moments and
step counters in only one arm. All four actual-gradient controls passed in
both arms. Their final structure evaluations determine the next accuracy action.

A CPU-only [reference-free selection screen](reports/consensus_final_ema.md)
raised TM from 0.56824 to 0.57367 by choosing the most mutually consistent of
three predictions. The selector sees predicted coordinates only. This is a
development result below the +0.01 promotion threshold. The
[two new inference-noise replications](reports/consensus_49528311.md) give
TM gains of +0.00352 and +0.00368. Their pooled gain, excluding the initial
screen, is +0.00360 [95% cluster interval +0.00219, +0.00507]. This is a
consistent modest benefit on reused targets, not independent-target or
training-seed confirmation. No independent-test structures have been scored.
The CPU-only [nine-sample diagnostic](reports/consensus_nine.md) reaches
0.57539 TM, +0.00353 over the three-sample selector's expectation, at three
times the head/decoder sample budget. It misses its accuracy threshold, so
no new nine-sample GPU generation is assigned. Best-of-nine by native TM
is 0.60614, an oracle upper bound that cannot be used for deployment.
The [existing length/continuity strata](reports/consensus_strata_final_ema.md)
show a smaller, uncertain selection benefit for the longest chains.
The same rule improves pair-free to 0.56230 TM, but it remains
[0.01137 below selected pair](reports/consensus_pairfree_vs_pair.md)
(95% cluster interval −0.01515 to −0.00763). No GPU follow-up is assigned to
that branch: it fails development noninferiority despite its within-model gain.

The [checkpoint diagnostic](reports/checkpoint_49524706.md) supports retaining
final EMA: training-selected epoch-22 EMA changes TM by −0.00057 (uncertain),
and final raw weights by −0.00359 (interval entirely negative). Its geometry
report was corrected to use only the matching 25-step/CFG-2 reference rows;
TM and lDDT were already filtered correctly. The
[pair-only recomputation attempt](reports/efficiency_49526739.md) failed the
predeclared gradient-equivalence control before timing and is not adopted.

The current autonomous window ends at 2026-10-01 13:30 UTC (09:30 EDT).
New requests receive a Slurm completion deadline. A one-shot project timer
also cancels any unfinished requests from this window at its end, covering
the jobs submitted before that scheduler deadline was added. Its ownership
filter uses only this project's registry and submission timestamps.

The [complete sequence-to-backbone pipeline](reports/online_49470256.md) now
includes fresh final-layer ESMC extraction, with all components in strict FP32.
It scores 0.56767 TM and processes 1.19 proteins/s, returning three structures
per protein; peak reserved memory is 78.4 GiB. Computation measured 95.1% SM
activity and 75.1% instruction issue. Accuracy and coarse geometry pass the
development noninferiority checks against cached inference. These are inherited
development sequences, which can omit unresolved residues. The ESMFold2 timing
used a different batch regime, so no matched-throughput speed ratio is claimed.

The [FP16 ESMC and feed-forward-head candidate](reports/online_49537668.md)
passes the unchanged online numerical and development noninferiority checks:
TM 0.56784, 2.03 proteins/s, 66.6 GiB reserved, and 65.0% instruction issue
during collection. It is 1.71x faster than the matched full-FP32 online run,
below the predeclared 2x speed gate. A single
[larger-batch test](configs/online_batch_plan.json) uses that measured memory
headroom. A separate [AdamW implementation profile](configs/optimizer_profile_plan.json)
tests optimizer overhead with the validated all-block recomputation policy.
That [optimizer profile](reports/optimizer_49538855.md) found only 0.38–0.79%
speed gains and roughly 40–43% instruction issue; no kernel change is adopted.
The [larger-batch result](reports/online_49539818.md) uses 93.0 GiB for only
1.24% more throughput, so smaller FP16 batches remain preferred. Separate
tests now examine [conditioning reuse across samples](configs/online_reuse_plan.json)
and [20 rather than 25 flow steps](configs/online_twenty_plan.json), retaining
the same numerical and accuracy thresholds.
Those tests have now completed. [Conditioning reuse](reports/online_49542513.md)
improves FP16 throughput by 11.1%, lowers reserved memory to 55.2 GiB, and leaves
TM nearly identical. The [20-step screen](reports/online_49542864.md) measures
2.005x versus FP32 and passes the declared noninferiority limits: TM change
−0.0000013, CA lDDT −0.00134, and peptide-outlier fraction +0.000416.
The speed result is too close to 2x for a robust claim across separate GPUs.
A [combined candidate](configs/online_combined_plan.json) is being validated
before repeated timing on the same H200, including the fixed sample selector
in both candidate and reference pipelines.

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

LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib "$PYTHON" -m unittest discover -s tests -v
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

The prediction command uses cached embeddings. Its timing is labeled accordingly.
`scripts/benchmark_online.py` measures the complete pipeline including frozen
final-layer ESMC; the validated configuration is in `configs/validated_inference.json`.

## Scope and limits

- Tested: 47 CPU contract tests; exact forward parity of small pair and pair-free
  models against isolated original definitions; a real pretrained ProteinAE
  decoder on one validation target; the full 626-target artifact/data audit.
- H200 job 49346371 completed 50 throughput/memory configurations of the actual
  legacy heads and decoder. All eight real-weight cache equivalence checks gave
  exactly identical coordinates. Nsight counters are analyzed separately from
  nvidia-smi GPU busy time in `reports/h200_profile.json`.
- Nine sets of new weights were trained on 1,024 proteins and evaluated on
  reused development data. One geometry evaluation failed its shape control;
  neither accuracy recipe meets the declared promotion gate.
  The [independent test selection](reports/holdout_expanded_20260930.md) is now
  locked at 34 structures after a score-blind expansion to January 2024 releases.
  It contains 32 chains of at most 256 residues and only two longer chains;
  it cannot support a strong long-chain accuracy claim. All inputs preserve full
  polymer sequences and explicit observed-residue maps. No models have been
  scored on it, because neither development recipe passed promotion.
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

### October 1 execution-window close

All registered GPU jobs finished; the 09:30 EDT deadline closed with no cancellations needed. The combined inference screen reached 2.2806x throughput and 55.2 GiB reserved, with development accuracy changes inside its declared margins. A repeated comparison on the same H200, including native-free sample selection, remains necessary.

The four-shard benchmark and analysis are implemented in `scripts/benchmark_matched_online.py` and `scripts/summarize_matched_online.py`, with the frozen protocol in `configs/matched_online_plan.json`. The initial submission attempt was blocked by the sandbox and did not complete before the original deadline. After the user requested continuation and restored full access, the bounded follow-up was submitted as **49612272**, four H200 tasks with 22-minute limits. All four tasks ran at approximately 10:06 EDT on October 1. The [expanded numerical controls rejected the candidate](reports/matched_online_49612272.md): all 32 FP32 controls passed, but FP16 produced batch/single differences of 0.333 and 2.224 A RMSD on two additional proteins. The remaining two own tasks were cancelled before timing. No repeated speed or selected-accuracy result was produced. The earlier 2.2806x screen does not justify promoting this candidate. The existing 50 CPU tests and two new timing/selection validation tests passed. No GPU performance result is implied by those tests.

The completed training trace assigns roughly 69–72% of summed kernel duration to backward/clip. Copies, elementwise operations and layer normalization dominate long-sequence kernels; AdamW contributes less than 1%. These are profiling observations, not proof of a particular source-level optimization. The 34 independent-test structures remain unscored.

### Ensemble-first research (October 1)

The user approved [the ensemble research plan](configs/ensemble_research_plan.json), reopened ESMC layers 20/40/60/80, and authorized experiment-appropriate walltimes with at most eight GPUs running plus pending. The old campaign deadline no longer governs this work. The first [ProteinAE round-trip calibration](reports/roundtrip_49615375.md) completed on one H200: fresh encodings reconstructed 16 mapped training structures at mean CA RMSD 0.1781 A and CA lDDT 0.9994 using three decoder steps. Decoder-seed variation averaged 0.1964 A pairwise RMSD. This is adapter calibration, not evidence of experimental state coverage. Published reference assets are pinned and hashed; ensemble panel curation is underway.

The current four-arm training campaign has a fixed continuation timer, `esm-proae-reboot-checkpoint-followups.timer`. It queues the four predeclared 2,000-update ensemble evaluations through the normal eight-GPU cap and exact-job registry. `runs/checkpoint_followups_state.json` records progress. The completion watcher also starts bounded CPU state scoring after ensemble generation. Checkpoint follow-ups therefore continue across an interactive-session disconnect.
