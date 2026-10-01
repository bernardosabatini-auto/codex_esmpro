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
