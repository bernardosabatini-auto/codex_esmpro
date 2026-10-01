# Teacher-mode learnability and pose ablation

Authorized through October 2, 2026, 11 AM America/New_York (15:00 UTC), with at most eight project GPUs running plus pending. The submission guard now enforces the deadline. Only registered own jobs are inspected or modified. Completion monitoring remains active.

Selection is frozen before inspecting any student predictions: 32 members of the prior512 training set, eight per length bucket, ranked by teacher-defined contact-state count and dispersion. All32 selected targets have16 distinguishable valid teacher conformations. These are predicted modes, not biological states or equilibrium populations. All source labels and selection hashes are bound. Locked tests remain untouched.

The first capacity experiment uses pure uniform teacher supervision, rather than the previous50/50 reference mixture, against a reference-only arm. The two teacher arms differ only in fixed-reference versus independent-PCA encoding. Every reference latent remains bitwise identical to its inherited cache. Target order, label draws, initialization and stochastic training streams are matched. Planned2000updates, learning rate3e-5, checkpoints500/2000, fresh32-sample evaluation at CFG1 and CFG2. Preserve every result; no post-hoc guidance selection hidden from reports.

## Label audit first

Job49690071 encodes/audits all512selected conformations in both frames. Three-step decoding achieves mean CA-lDDT0.99597 aligned and0.99530 PCA, but coarse validity drops from1.0 at input to0.96094 and0.95117. Both fail the unchanged1-percentage-point reconstruction-validity margin. This deliberately difficult subset reveals an AE/decoder limitation that the full-corpus mean concealed. Training has not been launched through this failed gate.

Follow-up decision before seeing outcomes: repeat the same label audit with10 decoder steps, identical conformations and noise, before any training. Do not remove failed samples or relax thresholds. If it passes, the capacity experiment and its initialization baseline will both use10 steps; that would not justify a speed claim. If it fails, inspect reconstruction errors and decoder limitations before deciding whether a defensible capacity test remains possible.

## Pre-training revision to a reliable capacity panel

Ten decoder steps (49691755) improve validity to0.97461 aligned and0.98047 PCA but both still fail the unchanged gate. The extreme-diversity panel has mean teacher confidence0.705, range0.436–0.889, and13/32 targets lack the required confident core. Maximum teacher dispersion was the wrong priority for an easy capacity diagnostic. Both failed audits remain reported; no training was performed on that panel.

Before any student outcome is available, freeze a second panel using confident teacher conformations: mean pLDDT>=0.8, a confident core covering at least max(32,ceil(L/2)),2..8 contact states and mean contact-feature distance<=6A. Only five short proteins satisfy these rules, so take those five and the nine highest-confidence eligible proteins in each other bucket (32 total). Keep all16 conformations of every selected protein and audit both encodings at3decoder steps. This is explicitly a selected easy-capacity test, not a generalization benchmark. Source data, definitions and rejected-panel results are retained. Frozen protocol: `configs/overfit_reliable_protocol.json`.

## Validation and additional diagnostics

CPU checks confirm teacher self-recall and invariance of contact assignment under a proper rigid pose change. Unit checks confirm invalid geometry cannot count as a contact-state hit and identical teacher structures do not create distinct modes. The environment lacks pytest; the two test functions were executed directly with the existing environment, without installing packages.

Noise-time-binned velocity MSE is logged during training to distinguish poor early-flow transport from failures near a known target. No objective or random draws change for this diagnostic. The stricter1A contact-hit threshold is reported alongside the frozen2A primary threshold. CFG1 is the primary capacity comparison and CFG2 is retained as a sensitivity analysis (`configs/overfit_decisions.json`).

A read-only analysis of the previously failed20-step paired sampler found several non-neighboring CA distances near1–1.5A, including one below1A. Its failures are substantial collisions, not merely floating-point changes at a validity threshold. No threshold relaxation or unvalidated structure repair is adopted.

The reliable panel retains the pose effect being tested: median additional PCA frame angle10.40degrees,22.85% of conformations exceed90degrees, and15/32 proteins contain at least one such change. Mean teacher confidence ranges0.822–0.967. Thus confidence selection did not remove the orientation discontinuity. Selection and pose summary arrays remain excluded from Git.

A read-only analysis of existing original-student25-step CFG2 latent samples on the frozen reliable panel finds mean nearest-teacher latent RMSE0.4254, teacher latent spread0.0625, and student latent spread0.2084. These quantities use a coordinate-dependent latent representation and are not structural accuracy measures. To separate pose from geometry, each capacity evaluation additionally re-encodes generated backbones before and after a single global fit to the cached reference. Those fits are diagnostic only: generated samples, scoring coordinates and inference remain unchanged. All frame comparisons still use identical evaluation code.

Read-only encoder inspection also clarifies the rotation verdict: coordinate components enter unconstrained learned linear layers, consistent with rotation-dependent codes. A deterministic canonicalization wrapper can make the composite encoding mapping invariant without retraining ProteinAE; changing that wrapper still changes the target convention for the pretrained prediction head. The earlier stronger wording has been corrected in `rotation_verdict_20261001.md`.

## Reliable-panel audit passed

Job49693246 completes the full512-conformation audit: mean CA-lDDT0.999111 for fixed-reference encoding and0.999091 for independent PCA; both decoded coarse-valid fractions are0.998047 versus1.0 at input. Both pass the original reconstruction gate. The fixed handoff submits40-update capacity profile49702037. No training input or sample was removed after this audit. Exact ESM-array and cached-reference-array identity checks precede training configuration preparation.

## Matched training submitted

Capacity profile49702037 completes40updates in81.99seconds of training with64.96GiB peak reserved GPU memory. Training SM issue is57.24%; whole-capture issue is20.12% because startup dominates this short profile. Do not describe the short allocation as meeting the50% whole-run goal. The longer runs amortize startup and will be measured separately.

The fixed handoff submitted reference49704029, aligned-teacher49704255 and PCA-teacher49704413, all from commit9be9139 with identical scientific code trees and configuration except arm. Each requests one H200,24GiB host memory,8CPUs and115minutes; the profile suggests roughly68minutes of training plus evaluation. The handoff timer stopped after all submissions; the completion watcher remains active. No manual duplicate submissions are needed.

The [Gaussian-bridge oracle diagnostic](overfit_teacher_bridge_20261001.md) uses only these teacher labels and simulated noise. At time0, per-coordinate conditional velocity variance is0.007592 aligned versus0.086632 PCA (11.4-fold), while the physical-mode prior is identical. By time0.5, oracle state classification is0.895 and0.919 respectively. This exposes nuisance variation and time dependence but does not establish a trained-model advantage. Actual matched training and structure evaluation decide that question.

## Oracle transport positive control

A separate diagnostic uses the exact empirical-teacher Gaussian-mixture velocity field, with identical fresh Gaussian seeds, ordinary Euler integration at5/10/25/100steps, the same final per-residue layer normalization, and3-step decoding. Both frames and all32 proteins are retained. CPU preparation takes6.7seconds. Single-teacher endpoint and orthogonal latent-transform controls pass. This oracle knows every teacher latent and is explicitly not a deployable sequence predictor. Its role is to show whether correct velocity fields can recover valid teacher modes through this sampler/decoder, separating a learned-head failure from an integration or representation limitation. It does not replace or alter the three matched training runs.

Oracle transport job49708850 completed successfully. At25Euler steps, aligned latents recover96.92% of teacher-defined states and independent PCA recovers91.95%, with99.90% coarse-valid decoded samples in both cases. At100steps these are96.92% and92.40%; the aligned result has already plateaued by25steps. This single shared seed set demonstrates high attainable teacher-mode recall through the existing sampler and decoder; it is neither a learned-model result nor evidence for biological population recovery. The expected recall from32 direct independent teacher draws is94.51%; a realized finite seed set can exceed that expectation. See [full control](oracle_transport_49708850.md).

## Verified shared initialization

All three completed baseline evaluations match, including sample state assignments. At CFG1, teacher-mode recall is 0.74747 with coarse validity 0.99219; at CFG2 recall is 0.56741 with validity 0.99121. Strict 1 Å recall is 0.50446 and 0.35729. Both guidance settings remain reported; CFG1 was declared primary before training. See [baseline comparison](overfit_comparison_0.md).

The CFG1 nearest-teacher latent RMSE is 0.44329, whereas re-encoding globally aligned predicted backbones gives 0.13363. At CFG2 these are 0.43580 and 0.11507. Decoder-to-encoder RMSE is about 0.0055. Much of the raw latent discrepancy is therefore associated with global pose; the alignment is diagnostic only and does not alter any generated prediction or structural score.

Posterior-target profile job49712994 tests the cost of an objective-preserving reduction in target noise, using one H200 for 40 updates. The [declared plan and equivalence tests](posterior_target_plan_20261001.md) precede any full training with that estimator.

## Posterior-target profile passed

Job49712994 completed 40 updates in 80.88 seconds with 64.72 GiB peak reserved memory, compared with 81.99 seconds and 64.96 GiB for the ordinary aligned-target profile. Training SM issue was 58.05%; whole-capture SM issue was 21.69%. Startup dominates the short capture. Sparse logged conditional variance averaged 0.002203, or 3.43% of the logged objective; this is not a measurement of gradient-variance reduction. The method is computationally viable, but its expected benefit appears modest and no full posterior-target training has been launched. See [profile](overfit_49712994.md).

A live check caught terminal accounting while a completed job still appeared as COMPLETING in Slurm. Scheduler queries now always consult the live queue for exact registered IDs and give live allocation state precedence. Regression tests cover the race and fail closed on a live-query error; a real query of all 30 nonterminal-registry IDs found exactly the three running training jobs, with none missing. No cap violation occurred.

Before any 500-update scores were available, comparison reports were extended to display paired family-bootstrap intervals and explicitly evaluate the already-declared capacity screen: recall gain at least 0.10 versus reference, positive recall interval lower bounds versus reference and initialization, and no more than 0.01 loss in validity versus initialization. The label manifest hash binds the family mapping. All 32 targets belong to distinct frozen families, so making that mapping explicit leaves existing baseline intervals unchanged. Intervals are unadjusted; an intermediate pass is provisional and a final capacity pass is not model promotion.

## Finite-sample calibration of the oracle control

A CPU simulation of 100,000 repeated experiments, each drawing 32 empirical teacher labels independently for each of the 32 proteins, has mean recall 0.94526 versus analytic expectation 0.94512. Its central 95% repeated-sampling range is [0.89940, 0.98333]. Both aligned and PCA 25-step oracle results lie inside that range. This is a distribution of repeated finite-label draws, not a confidence interval on biological populations or a paired test between frames. The 0.9692 versus 0.9195 oracle point difference must not be presented as proof of an alignment advantage. The control establishes attainable recall; actual matched learning comparisons address the training question. Reproduce with `scripts/diagnose_teacher_sampling.py`, seed2026100171.

## Larger-batch throughput profile

The measured 64.96 GiB peak of the ordinary profile leaves room within the existing 110 GiB capacity gate. A single-H200, 40-update profile will test batches64/32/16/12 at padded lengths128/256/384/512, versus32/16/8/8 previously. Its purpose is throughput and memory measurement only; changed batch sizes do not constitute a matched optimization experiment. Compare processed samples and padded residues per training second, not update time alone. Keep the three active training arms unchanged and use any accepted batching change consistently in future matched experiments.

Larger-batch profile submitted as job49716889, one H200 with a 10-minute walltime. No new full training arm is submitted while the 500-update comparisons remain incomplete.
