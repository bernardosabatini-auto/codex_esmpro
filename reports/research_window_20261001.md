# October 1 research results and bounded follow-up

The original window closed at 09:30 EDT. After the user requested continuation and restored full access, job 49612272 ran the prepared four-H200 confirmation attempt. It stopped at a numerical failure before any timed pass. All registered work is terminal and analyzed. The task-accounting audit covers 21 October 1 task IDs, with a maximum of eight GPUs pending plus running and zero remaining. Only registered project jobs were queried or cancelled.

## What the evidence supports

- **No improvement from the tested training continuations.** Optimizer beta, residue weighting, broader sampling and restored optimizer history failed their promotion criteria. Retain the untouched final EMA. The restored-history versus fresh-history TM change was -0.000016, with a confidence interval spanning zero.
- **Three-sample selection offers a modest accuracy gain.** The frozen native-free CA-lDDT medoid gained about 0.0036 TM in two additional inference-noise runs on the same development proteins. These are not independent target or training-seed replications. Nine-sample selection improved further but missed its predeclared follow-up gate and requires more generation.
- **The fastest precision candidate is not qualified.** Its initial 626-target screen measured 2.2806x throughput and 55.2 GiB reserved. The subsequent four-shard attempt tested additional batch/padding controls: all 32 FP32 controls passed, but the FP16 candidate had 0.333 and 2.224 A batch/single RMSD differences against a 0.2 A limit. The latter also changed native CA lDDT by 0.0101, exceeding 0.005. The two remaining tasks were cancelled before timing. No repeated speed or selected-accuracy result exists for that attempt.
- **Training efficiency remains unresolved.** Instruction issue is around 41% despite roughly 95% SM activity. The CUDA trace assigns about 69–72% of summed kernel duration to backward/clip, with substantial copy, elementwise and layer-normalization cost. AdamW is below 1%; fused AdamW only improved throughput 0.38–0.79%. The profile does not yet identify a validated source-level fix.

## Next experiment

Use a small diagnostic on the two failed development proteins to isolate FP16 ESMC, FP16 head operations, conditioning reuse and padding effects against the passing FP32 reference. Record both embedding and coordinate deviations with identical noise. Keep the existing numerical thresholds. A precision policy must pass those cases before another full timing attempt. This diagnostic is proposed, not submitted.

For training speed, map the expensive copy and normalization kernels back to the pair-module operations before changing layouts or compiling modules. Require numerical and gradient controls before adopting an optimization. Earlier ESM layers remain deferred.

## Scope and provenance

The 34 locked independent-test structures remain unscored; their manifest hash is unchanged. Development sequences, inherited checkpoints and external benchmark comparisons retain the limitations documented in the individual reports. No robust twofold speed claim or independent accuracy improvement is established. Data, weights, predictions and raw traces remain excluded from Git.

Key evidence: [precision rejection](matched_online_49612272.md), [initial combined speed screen](online_49544240.md), [training kernels](kernels_49545063.md), [optimizer history](optimizer_state_49540968.md), and [selection noise replications](consensus_49528311.md).
