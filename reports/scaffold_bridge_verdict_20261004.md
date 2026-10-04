# Fixed-scaffold bridge: failed physical feasibility

Job50385481 completed the prospectively fixed2,000 updates. The entire generated
panel remains in the denominator:32 training-diagnostic proteins ×4 original
noises, including15 cases previously shown to have geometric obstructions.

| Arm | Raw coarse-valid | All eight-flank edges valid | After closure: full eligible geometry |
|---|---:|---:|---:|
| Trained generated |20/128|0/128|0/128|
| Untrained generated |0/128|0/128|0/128|
| Trained native context |25/128|0/128|Not part of this closure assay|

CPU closure increased trained coarse validity to29/128. Only1/128 passed the
narrower complete local gate, and that case failed the independently required
eight-flank edge check. The matched historical baseline passes30/128 under this
same complete gate. Paired difference:−23.44 percentage points; family bootstrap
95% interval[−32.03,−14.84]. These are reused training diagnostics, not generalization.

Technical checks passed: all2,000 draws match the previous runs, first40 raw/EMA
weights exactly reproduce the profile,330 integration calls preserve the fixed
state, and256 independently audited coordinate groups have maximum fixed-atom
error0.0000153Å. This is a scientific failure, not a missing-output failure.

## What failed

The requested motif and far scaffold are imposed and stay fixed. Their retention
does not demonstrate learned accuracy. Geometry collapses inside the rebuilt
residues, including when the surrounding scaffold is native:

| Rebuilt-region metric | Generated context | Native context |
|---|---:|---:|
| Peptide outliers / checked edges |1737/2304|1736/2304|
| CA gaps above4.5Å |276|228|
| Mean N–CA length |0.883Å|0.950Å|
| Mean CA–C length |0.992Å|1.030Å|
| Mean C–O length |0.566Å|0.624Å|

The intramolecular contraction suggests that independent Cartesian coordinate
prediction is averaging incompatible local conformations. This is a hypothesis,
not an identified cause; optimization or sampler error may also contribute.
Native-context failure prevents attributing everything to incompatibility between
the generated scaffold and the supplied fragment.

Close this fixed recipe. Do not refold it, extend this checkpoint, substitute a
partial gate, or reinterpret its imposed motif fit as scaffolding success.

## Next discriminating work

Before another panel-scale training run, implement and CPU-validate an internal
coordinate reconstruction for local N/CA/C/O bridges. First establish exact native
round-trip, proper rigid-motion behavior, fixed-anchor retention, gradients, and
explicit endpoint residuals. Hold bond lengths/angles to the source geometry while
allowing backbone torsions to vary; preserve the original motifs as separate fixed
atoms. A valid local representation alone cannot ensure closure, steric feasibility,
or designability. Endpoint constraints must be checked, not hidden by atom clamping.

If these prerequisites pass, specify a small native-context capacity comparison
before spending on a new2,000-update model. Require physically connected outputs
on this easy control first. Generated-context and same-refold motif/global/scaffold
evaluation follow only after capacity is demonstrated. This changes the output
representation; it does not relax the failed candidate's gates or replace its results.

## Cost and reproducibility

One RTX allocation13:06; training690.12s; worker769.62s; peak reserved37.17GiB.
All256 CPU closures took155.92s after release. Captured DCGM737s:51.01% weighted
utilization,85.66%SM,58.13%DRAM,94.03%GR and0%tensor. Excludes startup and is not
the account24-hour metric. No other agents' jobs were inspected.

Evidence: `fragment_inpainting_training_50385481.json`,
`scaffold_bridge_comparison_20261004.json`, `gpu_real_utilization_50385481.json`.
Source report SHA256:d6b769b04f62c606e7c90c0c232167ae15cbfb573db5ee766d45e6fa2ff9403d.
Immutable protocol: `configs/fragment_scaffold_bridge_protocol.json`.
