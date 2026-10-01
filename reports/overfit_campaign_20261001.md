# Teacher-mode learnability and pose ablation

Authorized through October 2, 2026, 11 AM America/New_York (15:00 UTC), with at most eight project GPUs running plus pending. The submission guard now enforces the deadline. Only registered own jobs are inspected or modified. Completion monitoring remains active.

Selection is frozen before inspecting any student predictions: 32 members of the prior512 training set, eight per length bucket, ranked by teacher-defined contact-state count and dispersion. All32 selected targets have16 distinguishable valid teacher conformations. These are predicted modes, not biological states or equilibrium populations. All source labels and selection hashes are bound. Locked tests remain untouched.

The first capacity experiment uses pure uniform teacher supervision, rather than the previous50/50 reference mixture, against a reference-only arm. The two teacher arms differ only in fixed-reference versus independent-PCA encoding. Every reference latent remains bitwise identical to its inherited cache. Target order, label draws, initialization and stochastic training streams are matched. Planned2000updates, learning rate3e-5, checkpoints500/2000, fresh32-sample evaluation at CFG1 and CFG2. Preserve every result; no post-hoc guidance selection hidden from reports.

## Label audit first

Job49690071 encodes/audits all512selected conformations in both frames. Three-step decoding achieves mean CA-lDDT0.99597 aligned and0.99530 PCA, but coarse validity drops from1.0 at input to0.96094 and0.95117. Both fail the unchanged1-percentage-point reconstruction-validity margin. This deliberately difficult subset reveals an AE/decoder limitation that the full-corpus mean concealed. Training has not been launched through this failed gate.

Follow-up decision before seeing outcomes: repeat the same label audit with10 decoder steps, identical conformations and noise, before any training. Do not remove failed samples or relax thresholds. If it passes, the capacity experiment and its initialization baseline will both use10 steps; that would not justify a speed claim. If it fails, inspect reconstruction errors and decoder limitations before deciding whether a defensible capacity test remains possible.
