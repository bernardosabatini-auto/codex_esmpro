# Completed ensemble-first campaign — 1 October 2026

**No trained candidate qualifies for promotion.** The student can generate meaningful latent-driven alternatives, and the teacher supplies additional valid reference states. The tested training changes did not improve aggregate state coverage. The current student is also slower than the teacher for ensembles. More training time alone did not solve either problem.

## What worked

ProteinAE preserves alternative experimental structures: mean reconstruction CA lDDT 0.9996 and state identity retained in the round-trip test. Decoder noise alone adds little useful diversity; the latent sampler is the useful source.

Teacher coverage on sixteen multi-state development families reaches 59.375% at 32 samples and 71.875% at 128, compared with the student's 43.75% at 32. The 32-to-128 teacher gain is 12.5 percentage points, family-bootstrap 95% interval [3.125,25.0]. All four improving cases are exact-sequence cases; restricting to thirteen exact-sequence cases gives a 15.38-point gain [3.85,26.92]. These are observed-state recovery results, not equilibrium population estimates.

Earlier ESMC layers contain probe-accessible signal: layer 60 beat layer 80 in a linear probe. But the trained layer-60 conditioner reduced state coverage to 40.625%; the learned layer mixture did not establish an accuracy improvement. Neither merits more expensive replication.

## What the four matched training arms showed

Each arm trained the full flow head for 2,000 updates on the same 512 families. Teacher arms used sixteen sampled teacher structures per family, with 50% AFDB-reference labels and 50% teacher labels. ProteinAE and ESMC stayed frozen. Both 500- and 2,000-update checkpoints received the predeclared 48-protein ensemble evaluation.

Final-checkpoint results:

| Labels | Coverage at 32 | Coarse validity | Nearest-reference CA lDDT | MD projected W1, lower better |
|---|---:|---:|---:|---:|
| Inherited baseline | 0.43750 | 0.99414 | 0.86794 | 0.48850 |
| Raw reference | 0.40625 | 0.97982 | 0.86366 | 0.47565 |
| Canonical reference | 0.43750 | 0.98177 | 0.86446 | 0.46818 |
| Canonical + empirical teacher | 0.43750 | 0.98633 | 0.86800 | 0.46132 |
| Canonical + balanced teacher | 0.43750 | 0.98763 | 0.86760 | 0.46628 |

Both teacher arms trade gains and losses between families, with zero aggregate coverage change and 95% intervals [-0.125,0.125]. Neither meets the predeclared gain of at least 0.10 with a positive lower confidence bound. No training-seed replication or confirmation scoring was triggered.

Empirical teacher training improves MD W1 over initialization by 0.02718 [0.01206,0.04378], but its additional improvement over canonical-reference retraining is only 0.00686, interval [-0.00621,0.02088]. Therefore the MD change cannot be confidently attributed to teacher ensembles. It also cannot substitute for the failed primary coverage result.

On 64 separate tuning families, empirical CA lDDT rises from 0.78384 to 0.78694; the gain interval includes zero. Optimized fixed-correspondence TM is effectively unchanged: 0.68488 to 0.68409, difference interval [-0.00708,0.00588]. The larger drop in the Kabsch-based TM diagnostic is alignment-sensitive and must not be presented as an equivalent optimized-TM loss. Teacher labels help relative to the weaker canonical-reference control, but do not establish an improvement over the starting model.

## Subsequent provenance correction

The original inherited cache already used PCA canonicalization before encoding. Fresh raw-file reference labels did not preserve that convention; this was missed in the initial interpretation. Both raw-file and first-residue-frame retraining changed the cached target convention. The corrected follow-up will preserve cached reference latents exactly and align teacher conformations to cached reference coordinates. See [the rotation verdict](rotation_verdict_20261001.md). The measured results above remain unchanged.

## Why the next experiment must change

ProteinAE latents depend strongly on arbitrary rigid rotation. Canonicalization removes this nuisance but changes the target convention of the inherited head. A useful next control is teacher structures rigidly aligned to their own training reference before encoding, retaining the raw reference latents. A proper-rotation alignment helper is implemented and CPU-tested; that new training experiment has not been launched.

The present cluster balancing is a weak proxy for useful state diversity. In 238/512 training proteins, all sixteen teacher samples are singleton RMSD clusters, making balanced sampling identical to uniform sampling. Restricting comparison to a shared confidence core reduces mean cluster count from 10.14 to 7.64 among 434 eligible proteins. Prioritize confidence-aware core/contact features before buying many more teacher samples. These exploratory findings did not change the frozen experiments.

## Speed and resources

Matched resident-model sequence-to-backbone latency on eight proteins, three repeats: student/teacher seconds are 0.831/1.389 for one structure, 2.236/1.820 for eight, and **7.302/3.859 for thirty-two**. The student has no current ensemble speed advantage. Teacher confidence heads were omitted with full-fold coordinate parity checks. Arbitrary reductions to 5 or 10 student flow steps fail quality gates; 20 steps narrowly misses the predeclared noninferiority bound. A learned shorter sampler is the next speed hypothesis, with actual end-to-end timing required.

The four training runs each took about 69 minutes on one H200 and reserved 63.65 GiB at peak. Three have valid full-run counters showing 59.6–59.9% SM instruction issue and 60.3–60.6% during training. The fourth has incomplete counter coverage and no utilization claim. This clears the 50% instruction-issue target where measured, but is not 60% peak FLOP efficiency. All eight intermediate/final ensemble follow-ups completed under the eight-GPU running-plus-pending cap. Only registered project jobs were inspected and managed. No GPU or CPU scoring work remains outstanding.

## Limits and disposition

This is development evidence. Most benchmark constructs overlap inherited training/development families, despite isolation from the new 512-family training set. AFDB training references are predictions. The reserved seventeen-case ensemble panel and original thirty-four-target independent test remain unscored. The reserved MD panel has only one family; metadata auditing found potential ATLAS expansion candidates but none disjoint from the inherited corpus.

Keep the inherited model as baseline. Next prioritize the reference-aligned teacher-label control, a training-versus-development capacity assay, and learned sampler compression. The detailed follow-up design is in [next_experiments_after_ensemble_pilot.md](next_experiments_after_ensemble_pilot.md). Code, protocols and aggregate reports are synchronized to Git; data, embeddings, weights, predictions and raw results are excluded.
