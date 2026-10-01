# Ensemble research: evidence and next experiments

The student has useful latent-driven diversity, but no new training intervention has yet improved it. The strongest actionable finding is that ProteinAE latents depend strongly on rigid rotation. We are testing whether removing that nuisance variation makes sequence-conditioned learning easier.

## Results

- ProteinAE reconstructs alternative experimental states accurately: CA lDDT 0.9996 and nearest-state identity retained for all tested states at three decoder steps. Increasing to ten steps has little benefit.
- On sixteen development multi-state families, student contact-state coverage rises from 28.1% at one sample to 43.8% at sixteen, then plateaus at thirty-two. Changing decoder noise alone stays at 28.1%. Prioritize latent sampling.
- Corrected ESMFold2-Fast reaches 59.4% coverage at thirty-two and 71.9% at 128 samples. The latter adds 12.5 percentage points, family bootstrap 95% interval [3.125,25.0] points, four improving families and twelve ties. The first thirty-two predictions were checked against the previous run. This establishes additional recoverable reference states, not equilibrium populations.
- Teacher versus student at thirty-two samples: +15.625 points, interval [6.25,28.125]. Three reference cases include up to two substitutions in one experimental construct; the exact-sequence thirteen-case sensitivity remains positive: +19.23 points, interval [7.69,30.77]. Reference environmental conditions also differ.
- Teacher 25/50/100 diffusion-step pilot found equal multi-state coverage on its four eligible proteins. Fifty steps is retained; a longer trajectory is not justified by this small pilot. Eight independently sampled trunks also did not add coverage on that pilot.
- Layer 60 beats layer 80 in a matched linear latent probe on 64 reserved probe families: CA lDDT 0.2418 versus 0.1792, paired gain 0.06256, interval [0.05223,0.07293]. Absolute quality is poor; this is evidence of accessible signal, not a usable structure predictor.
- The final-layer bounded residual conditioning control slightly worsened mean CA lDDT, 0.78384 to 0.78190 after 500 updates. Training SM instruction issue was 59.26%, whole capture 55.72%, peak reserved memory about 52 GiB. Matched layer-60 and learned-mixture arms are submitted.
- Sixteen training backbones under eight proper rotations: raw latent RMSE 0.98927, despite decoded CA RMSD 0.3361 A. A first-residue N/CA/C frame reduces latent RMSE to 0.00000198, with reconstruction RMSD 0.3516 A. Translation alone is effectively removed already. Canonicalization preserves internal geometry and chirality; its effect on learned accuracy remains untested.

## Consequent experiments

Generate sixteen teacher samples for each of 512 family-isolated training sequences, with reference and teacher labels encoded in the same canonical coordinate frame. Retain raw reference latents for a matched pose-preprocessing control. Profile the first 128-sequence shard before scheduling the other three. Preserve all samples and record a coarse geometry mask and native-independent structural clusters.

Then compare raw-reference-only, canonical-reference-only, canonical-reference plus empirical teacher samples, and canonical-reference plus cluster-balanced teacher samples. Keep data, initialization, update counts and sampling settings matched. These are flow-head training experiments; canonical labels may require adaptation of the inherited head. Do not infer training success from latent MSE alone. Evaluate decoded accuracy, validity and state coverage. Replicate eligible improvements with three training seeds before promotion.

A first-residue frame is deterministic but depends on local anchor geometry. The pilot must check reconstruction and learned behavior before treating it as a settled preprocessing choice. Cluster balancing also changes the teacher distribution deliberately; cluster frequencies are not thermodynamic probabilities.

## Limits and resource policy

This is development evidence. 119 of 122 eligible benchmark constructs overlap inherited training/development families. The 512 new training families exclude the reference panel, but that does not erase inherited-head exposure. AFDB reference labels are predictions, not experimental native conformations. The reserved ensemble confirmation panel and original 34-target independent test remain unscored; only one MD confirmation family is available, insufficient for a strong MD generalization claim.

The earlier teacher path incorrectly activated an untrained MSA branch. It is quarantined. The corrected 626-target external comparison gives mean TM 0.599825 for teacher versus 0.568238 for student, paired gain 0.031587, family interval [0.024814,0.038628]. No full upstream-port parity claim is made.

Matched end-to-end ensemble timing is still needed. Existing teacher sampling and student flow timings cover different stages, so they do not establish a student speed advantage. Measure sequence-to-ensemble cost, first-sample latency and marginal sample cost before claiming efficiency.

At most eight registered project GPUs running plus pending. Each new workload is profiled on one H200. Only registered project jobs are queried or managed. Completion watchers run every minute, with automatic result summaries. Code and written reports are synchronized to Git; generated data and weights remain excluded.
