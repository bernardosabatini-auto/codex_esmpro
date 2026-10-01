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
