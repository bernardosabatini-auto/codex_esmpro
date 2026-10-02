# Generative capability: what survives a stricter assay

The model can generate diverse, plausible backbones and preserve a supplied motif in generated coordinates. We have not yet demonstrated useful isolated-fragment scaffolding under a sequence-design/refolding test that also checks the motif itself. These experiments use development panels; no locked tests were scored.

## Contact guidance through initial noise

The original50-step flow and frozen decoder pass forward identity, directional finite differences and checkpointed/direct gradient controls. Eight fixed cases compare up to12normalized-gradient updates against the best contact match among33random candidates, using only the supplied contact objective for selection. Every generated failure is retained.

| Method | Contact within1A | Full-backbone valid | Best8designable | Generated joint success | Joint success also retained after refolding | Generation/search seconds |
|---|---:|---:|---:|---:|---:|---:|
| Initial single sample | 0/8 | 8/8 | 6/8 | 0/8 | 0/8 | 3.49 |
| Noise guidance | 5/8 | 8/8 | 6/8 | 4/8 | 2/8 | 168.06 |
| Random candidate selection | 3/8 | 8/8 | 6/8 | 3/8 | 3/8 | 41.27 |

Guidance is numerically valid but does not earn its cost for this contact task. The matching6/8designability counts are too small to prove no regression. Generation timing excludes model loading, numerical controls and designability assays; no end-to-end speed claim. Peak reserved GPU memory was8.34GiB. See [generation](noise_guidance_49863415.md), [224refold assay](noise_designability_49863726.md) and [constraint retention](refold_constraint_retention_20261002.md).

## Isolated fragments expose a real limitation

The earlier motif codes came from complete structures. We instead cropped each motif first, canonicalized using only that fragment and encoded it as a standalone chain. Same original50step/RePaint3recipe,16families/four paired seeds, unchanged noise streams; all controls passed.

| Motif code source | Motif dRMS | Motif within1A | Full-backbone valid |
|---|---:|---:|---:|
| Complete native structure | .390A | 64/64 | 43/64 |
| Isolated fragment | .417A | 64/64 | 26/64 |

Validity drops26.6percentage points; paired-family95%interval[-42.2,-12.5]. This comparison changes context, frame and encoder positions together; it cannot attribute the loss to one of them. Standalone fragment roundtrips average.124A distance RMS, so failure is not simply inability to reconstruct the supplied fragment. All57nonlocal CA clash pairs in isolated outputs involve motif–scaffold contacts;39of68CA gaps are at motif boundaries. See [generation](isolated_motif_49864561.md) and [failure localization](fragment_failure_diagnostic_20261002.md).

On the fixed four-family/two-seed ProteinMPNN panel, free sequence design gives3/8joint successes for full-context codes and2/8for isolated codes. Requiring the SAME designed sequence to refold with acceptable global agreement, valid geometry and motif dRMS<=1A reduces both to0/8. A global scTM>.5does not establish local motif preservation. See [160refold assay](fragment_designability_49865077.md).

## Fixing the motif sequence is necessary to test, but is insufficient here

We repeated the identical20backbone assay, fixing only the supplied motif amino acids in ProteinMPNN; all scaffold positions remained freely designed. All160refolds, fixed residues, positive controls and repeatability controls were audited.

| Motif code source | Strict joint, free sequence design | Strict joint, motif residues fixed |
|---|---:|---:|
| Full context | 0/8 | 2/8 |
| Isolated fragment | 0/8 | 0/8 |

This is a small feasibility result, not a population success rate or experimental validation. It strengthens the need to assess constraint retention after sequence design, and leaves the practical isolated-fragment task unsolved. See [matched fixed-sequence assay](fixed_motif_designability_49866072.md).

## Noise-space motif optimization also failed

None of264existing random candidates matched these isolated motifs within1A. A frozen eight-case experiment therefore starts from each case's best random candidate and optimizes initial noise through the original flow using a motif distance-matrix objective. It uses the same12update/line-search recipe, unchanged numerical controls and no motif-code insertion. Any follow-up must retain the fixed motif sequence and the strict same-sequence refolding gate. No outcome-driven parameter grid is authorized by this protocol.

The completed eight-case test passed every numerical check but reached0/8motifs within1A. Mean motif dRMS changed4.463→4.380A, with both starts and endpoints8/8coarse-valid. Accounting for initial random search, cost increased41.27→342.30seconds. The frozen recipe is closed without a designability follow-up or parameter grid. See [motif noise guidance](motif_noise_guidance_49867032.md).

## Refinement-history ablation also closed

The inherited refinement recipe retains one self-conditioning estimate across inner refinements. Refreshing it after every inner evaluation, with the same weights, noise, times, isolated-fragment codes and148velocity evaluations, did not help. Raw joint success changed26/64→24/64: difference−0.03125,95%family interval[−0.140625,0.09375]. All64motifs still met1A fidelity. This recipe failed its predeclared gate and received no designability follow-up. See [completed history ablation](motif_history_49868443.md).

## Pair-free unconditional generation is not materially faster in this profile

The corrected r4b pair-free checkpoint and original pair model both produce64/64coarse-valid backbones on the same16families/four noises. All128outputs and8CFG0/null controls pass; the64original outputs reproduce the historical archive. Generation-only times are11.06s versus10.78s, peak3.83/3.84GiB. The unconditional sampler already skips sequence-conditioned pair computation. Therefore the reported3.5xtraining-step benefit cannot be carried over to this path. These one-pass timings do not establish a small speed difference, and no pair-free designability assay has been run. See [corrected pair-free profile](pairfree_generation_49880198.md).


## Explicit isolated-fragment training: first completed comparison

The new open-ended generation campaign trained a zero-initialized fragment adapter on32existing training proteins with nine standalone fragments each. Inputs were only cropped fragment latents, supplied motif amino acids and placement; no scaffold sequence, ESM embedding or output-latent clamping. Adapter-only and full-network arms used identical initialization, data and random draws for2000updates. All2304saved predictions were audited.

Neither arm passed its prespecified capacity gate. Adapter-only had0/128training joint successes. Full-network had6/128with conditioning versus1/128with the fragment dropped: a3.9percentage-point difference with paired-family95%interval[0,8.6]. Both produced0/64development joint successes. Lower average motif error is not adequate constraint retention.

The subsequent fixed-motif ProteinMPNN/refolding assays each retained36backbones and288refolds. The same single refold had to match the scaffold globally, pass geometry and preserve the motif under both distance RMS and proper-rotation CA RMSD thresholds of1A.

| Conditioner | Valid globally agreeing refold, motif sequence fixed | Strict motif/global/geometry success |
|---|---:|---:|
| Token adapter only |2/8|0/8|
| Token adapter plus full network |4/8|0/8|

These are four-family development feasibility results. The difference in global designability is uncertain, and neither method solved motif scaffolding. Shared control sequences were identical; refolds differed slightly numerically (maximum CA RMSD0.00967A,lDDT1), within the established teacher repeatability tolerance, with the same control decisions. Experimental scaffolds gave4/4valid global refolds and3/4strict successes; fixing their motif amino acids in a separate32refold calibration still gave3/4strict successes, with a different failing family. Thresholds and failed cases were retained.

A direct intramotif-distance conditioner is being tested next. Its first run stopped at500updates on a numerical pose control. A frozen-checkpoint diagnostic reproduced the failure and separated FP32coordinate rounding from exact rotation: FP64distance calculation plus exact rigid transforms produced identical latents on all four controls, while rounding changed backbone CA RMSD by at most0.001166A without changing validity. The failed run remains failed. The corrected fresh2000update restart completed with all24exact-pose controls passing and all1152outputs audited. Development motif dRMS fell to3.195A from6.596Afor the token-only adapter; all64development samples remained coarse-valid. Nevertheless, joint motif success remained0/64development and0/128training. All2000training draw traces matched the token-only baseline. Direct distances improve conditioning substantially but do not yet enforce the requested fragment.

See [training comparison](fragment_training_comparison_2000.md), [paired refolding](trained_fragment_designability_comparison.md), [fixed native positives](fragment_fixed_positive_49906292.md), and [numerical diagnostic](fragment_geometry_pose_49908661.md).

## Decoded motif supervision and stronger guidance did not solve retention

The decoded-motif auxiliary run **49921479** completed 2,000 updates with matched training draws and passing numerical controls. It bounded the auxiliary adapter gradient to half the flow gradient norm. Mean development motif dRMS fell from **3.195 to 3.004 Å**, but joint counts remained **0/128 training and 0/64 development**. Its prespecified improvement gate failed. The unchanged 288-refold assay is proceeding regardless of that failure.

The distance-only model completed its own 288-refold assay: **0/8 strict successes and 2/8 valid globally agreeing refolds**, with the supplied motif residues fixed during sequence design. That is the same global designability count as the token-only adapter, with substantial uncertainty across four families.

A single CFG2 screen also failed: mean motif dRMS improved to **2.329 Å** from 3.195 Å at CFG1, but both produced **0/64 strict raw matches**. CFG2 took 1.90 times as long. All 128 outputs remained coarse-valid. No strength sweep follows. Allowing reflections during a diagnostic alignment did not recover any sub-1 Å fit, so handedness alone does not explain the failures.

The separate full-network distance-conditioner run **49929751** passed its 40-update profile and is training. It tests whether the frozen generator limits how well it can use the fragment geometry.

## Designability optimization will use actual refold measurements

The next planned intervention collects feedback targets from eight existing training families. A qualifying target must be one valid refold that simultaneously fits the fragment and globally agrees with the generated scaffold. Thresholds and minimum label yield are fixed in [the feedback protocol](../configs/fragment_feedback_protocol.json). Development and locked-test proteins are excluded from those labels. A raw motif failure repaired by sequence refolding remains a failed retention sample; it can only become a separately identified training target.

An exploratory ProteinMPNN score diagnostic found no useful within-backbone sequence-ranking signal: mean Spearman correlation 0.010 across 24 generated backbones. Selecting the lowest global score produced **3/24** valid global refolds, versus **5/24** for the first sequence. This does not support likelihood-only training or a cheap designability selector. Results are exploratory and share four development families across three model arms.
