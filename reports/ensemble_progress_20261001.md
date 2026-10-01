# Ensemble research: evidence and next experiments

The student has useful latent-driven diversity, but no new training intervention has yet demonstrated a statistically supported improvement. The strongest actionable finding is that ProteinAE latents depend strongly on rigid rotation. We are testing whether removing that nuisance variation makes sequence-conditioned learning easier.

## Results

- ProteinAE reconstructs alternative experimental states accurately: CA lDDT 0.9996 and nearest-state identity retained for all tested states at three decoder steps. Increasing to ten steps has little benefit.
- On sixteen development multi-state families, student contact-state coverage rises from 28.1% at one sample to 43.8% at sixteen, then plateaus at thirty-two. Changing decoder noise alone stays at 28.1%. Prioritize latent sampling.
- Corrected ESMFold2-Fast reaches 59.4% coverage at thirty-two and 71.9% at 128 samples. The latter adds 12.5 percentage points, family bootstrap 95% interval [3.125,25.0] points, four improving families and twelve ties. The first thirty-two predictions were checked against the previous run. This establishes additional recoverable reference states, not equilibrium populations.
- Teacher versus student at thirty-two samples: +15.625 points, interval [6.25,28.125]. Three reference cases include up to two substitutions in one experimental construct; the exact-sequence thirteen-case sensitivity remains positive: +19.23 points, interval [7.69,30.77]. Reference environmental conditions also differ.
- Teacher 25/50/100 diffusion-step pilot found equal multi-state coverage on its four eligible proteins. Fifty steps is retained; a longer trajectory is not justified by this small pilot. Eight independently sampled trunks also did not add coverage on that pilot.
- Layer 60 beats layer 80 in a matched linear latent probe on 64 reserved probe families: CA lDDT 0.2418 versus 0.1792, paired gain 0.06256, interval [0.05223,0.07293]. Absolute quality is poor; this is evidence of accessible signal, not a usable structure predictor.
- The final-layer bounded residual conditioning control slightly worsened mean CA lDDT, 0.78384 to 0.78190 after 500 updates. Training SM instruction issue was 59.26%, whole capture 55.72%, peak reserved memory about 52 GiB. Layer 60 finishes at 0.78663 (+0.00279; family interval approximately [-0.00078,0.00771]), while the mixture ends at 0.78385. The layer-60 effect is uncertain; its completed ensemble follow-up below did not qualify for replication.
- Sixteen training backbones under eight proper rotations: raw latent RMSE 0.98927, despite decoded CA RMSD 0.3361 A. A first-residue N/CA/C frame reduces latent RMSE to 0.00000198, with reconstruction RMSD 0.3516 A. Translation alone is effectively removed already. Canonicalization preserves internal geometry and chirality; its effect on learned accuracy is being tested in the matched training arms.

## Consequent experiments

Generate sixteen teacher samples for each of 512 family-isolated training sequences, with reference and teacher labels encoded in the same canonical coordinate frame. Retain raw reference latents for a matched pose-preprocessing control. Profile the first 128-sequence shard before scheduling the other three. Preserve all samples and record a coarse geometry mask and native-independent structural clusters.

Then compare raw-reference-only, canonical-reference-only, canonical-reference plus empirical teacher samples, and canonical-reference plus cluster-balanced teacher samples. Keep data, initialization, update counts and sampling settings matched. These are flow-head training experiments; canonical labels may require adaptation of the inherited head. Do not infer training success from latent MSE alone. Evaluate decoded accuracy, validity and state coverage. Replicate eligible improvements with three training seeds before promotion.

A first-residue frame is deterministic but depends on local anchor geometry. The pilot must check reconstruction and learned behavior before treating it as a settled preprocessing choice. Cluster balancing also changes the teacher distribution deliberately; cluster frequencies are not thermodynamic probabilities.

## Limits and resource policy

This is development evidence. 119 of 122 eligible benchmark constructs overlap inherited training/development families. The 512 new training families exclude the reference panel, but that does not erase inherited-head exposure. AFDB reference labels are predictions, not experimental native conformations. The reserved ensemble confirmation panel and original 34-target independent test remain unscored; only one MD confirmation family is available, insufficient for a strong MD generalization claim.

The earlier teacher path incorrectly activated an untrained MSA branch. It is quarantined. The corrected 626-target external comparison gives mean TM 0.599825 for teacher versus 0.568238 for student, paired gain 0.031587, family interval [0.024814,0.038628]. No full upstream-port parity claim is made.

Matched end-to-end ensemble timing below establishes a current student disadvantage at K=32. Earlier unmatched timings must not be used to claim an ensemble speed advantage.

At most eight registered project GPUs running plus pending. Each new workload is profiled on one H200. Only registered project jobs are queried or managed. Completion watchers run every minute, with automatic result summaries. Code and written reports are synchronized to Git; generated data and weights remain excluded.

The first teacher-label shard completed 128 targets and 2,048 conformations, 2,041 coarse-valid. Canonical reference reconstruction averaged 0.1896 A CA RMSD; teacher sample zero averaged 0.1744 A. Peak reserve was 82.4 GiB, SM instruction issue 58.89% during generation and 50.44% across capture. Cluster balancing changes the conditional distribution for 43/128 targets (mean total variation 0.107 across all targets). Remaining shards use the same validated recipe.

The full-head FP32 capacity pilot completed 64 updates in 124.0 seconds, peak 65.0 GiB, training SM instruction issue 60.21%. Whole short capture was 40.68% because initialization dominates a short profile. Four 2,000-update arms will use 100-minute limits and a 95-minute work guard, with evaluation at 0/500/2000 and explicit coarse-geometry metrics.

The layer-60 ensemble follow-up failed the diversity gate: latent-driven contact-state coverage at 32 fell from 0.4375 to 0.40625; coarse validity fell from 0.99414 to 0.98893. MD projected W1 improved slightly, 0.48850 to 0.48440, but does not rescue the primary coverage result. No training-seed replication is scheduled for this branch. Final-layer conditioning remains fixed for the four pose/distillation arms.

Matched same-H200 resident-model sequence-to-backbone latency on eight development proteins (three repeats) gives student/teacher seconds: K1=0.8308/1.3887, K8=2.2360/1.8201, K32=7.3018/3.8591. Teacher confidence heads are omitted with full-fold coordinate parity checks; student output matches its prior sequence-to-ensemble output. Both use strict FP32. The student currently has a single-structure latency advantage and an ensemble latency disadvantage, while teacher state coverage is better. This does not establish an advantage for a fast generative student. Lower sampling cost is required alongside accuracy improvements.

All 8,192 teacher labels passed the full-corpus latent round-trip gate: mean CA lDDT 0.99959, mean CA RMSD 0.17843 A, minimum sample lDDT 0.93736; coarse validity decreased from 0.99573 to 0.99146, within the 0.01 margin. GPU audit metrics matched CPU references in every length bucket. Four matched 2,000-update training arms are running: raw reference, canonical reference, canonical plus empirical teacher, canonical plus cluster-balanced teacher. All 64 tuning coordinate maps are now independently verified against their AFDB source files.

The inherited-model sampling sweep rejected 5 and 10 steps. Five-step latent ensembles lost 0.06667 CA lDDT and 0.21029 coarse-valid fraction; their lower MD W1 is misleading without geometry checks. Ten steps lost 0.01789 CA lDDT and 3.125 percentage points of state coverage. Twenty steps retained identical state coverage and lost 0.00344 mean CA lDDT, but its family interval [-0.00509, -0.00197] narrowly misses the predeclared -0.005 noninferiority bound. No sampling shortcut is adopted. A trained shorter sampler is a more consequential next speed hypothesis than further small reductions in Euler steps.

Before any 500-update tuning result was available, the ensemble follow-up was expanded to both 500 and 2,000 updates for every arm. This supersedes native-accuracy-only checkpoint selection: the research objective includes generative coverage. Both endpoints and all arms will be reported; reserved confirmation and independent test remain quarantined.

## Matched 500-update checkpoint results

All four predeclared intermediate checkpoint ensembles and state scoring completed. No arm improved aggregate contact-state coverage over the inherited baseline.

| Training labels | Coverage at 32 | Coarse valid fraction | Nearest-reference CA lDDT | MD projected W1 (lower better) |
|---|---:|---:|---:|---:|
| Inherited baseline | 0.43750 | 0.994141 | 0.867936 | 0.488501 |
| Raw reference | 0.43750 | 0.990234 | 0.864225 | 0.480222 |
| Canonical reference | 0.43750 | 0.989583 | 0.864500 | 0.477344 |
| Canonical + empirical teacher | 0.43750 | 0.991536 | 0.867109 | 0.475973 |
| Canonical + balanced teacher | 0.40625 | 0.990885 | 0.867125 | 0.470266 |

Empirical teacher supervision improves tuning CA lDDT relative to the matched canonical-reference control by 0.00494 (95% family interval [0.00307, 0.00684]); balanced supervision improves it by 0.00427 [0.00184, 0.00653]. Neither establishes a positive tuning improvement over the inherited initialization. Tuning coarse validity also falls.

The empirical ensemble's MD W1 improves by 0.01253 [0.00433, 0.02196] relative to initialization, but coverage is unchanged with a wide paired interval. This is a secondary distributional effect, not successful diversity promotion. The current reserved MD panel has only one family. No training-seed replication or confirmation scoring is justified at this checkpoint. All four matched 2,000-update runs continue; their predeclared ensemble follow-ups are submitted automatically only after verified successful completion, under the eight-GPU guard.

Training-label sensitivity shows that 238/512 proteins have sixteen singleton RMSD components, making balanced and empirical sampling identical for those targets. Restricting the RMSD comparison to a shared teacher-confidence core reduces mean component count from 10.14 to 7.64 on 434 eligible proteins. This is evidence that uncertain regions contribute to the label dispersion, not a new state definition or a retrospective change to training. See `teacher_cluster_audit_20261001.md`.

The ATLAS metadata-only audit finds 63 eligible, current-panel-disjoint candidates but zero inherited-data-disjoint families. This can support a stronger intervention-held-out MD assay if needed, but cannot repair the inherited-training generalization limitation. No additional confirmation predictions were generated.

The full matched intermediate analysis also shows a global-accuracy loss: TM after Kabsch falls by 0.0165–0.0239 across the four 500-update arms, with paired family intervals entirely below zero. This is a fixed-correspondence diagnostic, not optimized TM-align. The teacher-supervised arms outperform the canonical-reference control but do not recover the inherited baseline's global accuracy. Local CA lDDT alone would conceal this tradeoff.
