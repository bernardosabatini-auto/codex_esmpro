# Next decisions after the ensemble pilot

Complete and report both predeclared checkpoints of all four matched arms before selecting an intervention. Promote only an arm with at least a 0.10 gain in valid state coverage at 32, a positive family-bootstrap lower bound, and acceptable decoded accuracy and validity. Replicate eligible effects with three training seeds before touching reserved confirmation. If none passes, preserve the inherited checkpoint as the baseline and report the pilot as negative. More iterations are not automatically justified.

## Preserve compatibility with the inherited latent pose

The existing raw-reference control retrains on raw AFDB latents, while both teacher-supervised arms use a new canonical pose for reference and teacher labels. Canonicalization removes arbitrary rotation, but also changes the target distribution relative to the inherited head. A negative canonical pilot would not distinguish teacher supervision from this adaptation burden.

The most direct additional pose control is to rigidly align each teacher backbone to its own AFDB reference before encoding, while keeping raw AFDB reference latents unchanged. Use a proper rotation fitted on a predeclared common confidence core, with explicit minimum coverage and fallback policy. The reference is training supervision; no reference structure is supplied at inference. Recheck all teacher latent round trips and internal geometry. Then train raw-reference plus aligned empirical teacher labels against the existing matched raw-reference control, using the same 512 families, noise streams, update schedule and evaluation checkpoints. This remains a hypothesis; it must not be described as a proven fix.

## Label-quality diagnosis

The training labels have substantial apparent dispersion from uncertain regions. Before increasing teacher sample counts or training scale, define a confidence-aware, core/contact-based representation using training labels only. Compare empirical sampling with this alternative under a matched reference-only control. Keep uncertainty masks distinct from geometry rejection; confidence is not correctness. State counts must not be inferred directly from global-RMSD connected components.

A useful next capacity assay would generate student ensembles on a data-only selected subset of training proteins, then compare their contact distributions with the stored teacher labels and matched held-out development results. Failure even on training proteins points to fitting/representation; success on training but not development points to transfer/data coverage. Freeze selection by sequence family, length and teacher-only label statistics before generating these student predictions. This assay diagnoses capacity; it cannot establish generalization.

## Learned sampling speed

The student takes 7.30 seconds versus the teacher's 3.86 seconds for 32 backbones on the matched resident-model benchmark. Reducing its existing Euler sampler to 5 or 10 steps breaks decoded quality; 20 steps narrowly misses the predeclared noninferiority bound. A learned shorter sampler is the appropriate next speed experiment.

Use the current 25-step guided student sampler as a fixed transport teacher, storing each Gaussian seed together with its resulting latent endpoint on training families. Fit a conditional reflow head to these coupled pairs, then evaluate 5/10 steps with guidance absorbed into the distilled target. Keep a matched independent-noise flow-training control and the unchanged 25-step sampler. Preserve multiple distinct seeds per sequence; never train against the average endpoint. This is a proposed application of [rectified flow](https://arxiv.org/abs/2209.03003), not a demonstrated protein result. [Progressive sampler distillation](https://arxiv.org/abs/2202.00512) supplies a related alternative if direct reflow loses quality.

A concrete first screen is 512 existing training families, 16 paired seeds per family, a single-H200 capacity profile, then matched 500/2000-update runs. Use strict FP32 first to avoid confounding numerical changes. Tune on the existing 64 families, then apply the frozen 48-protein ensemble metrics. Require preserved valid-state coverage and quality plus at least a twofold measured K=32 speedup over the current student; report comparison with the direct ESMFold2-Fast teacher as well. Benchmark actual sequence-to-backbone latency and marginal sample cost, including the decoder. Do not infer speed from step count. This speed branch has not been launched.

## Stronger distributional confirmation

The current reserved panel contains only one MD family. ATLAS metadata screening offers 63 families separate from the current experiment but all overlap inherited training/development data. Additional MD references can strengthen an intervention-held-out distributional test, not an unseen-family claim. Freeze sequence/coordinate maps, replicate-aware reference features, and target selection before candidate predictions. A negative state-coverage result is not rescued by selecting favorable MD targets.

All future jobs remain within eight project GPUs running plus pending, with exact registered-job monitoring and profiled workload-specific walltimes. Original independent-test and reserved confirmation predictions remain untouched until an eligible intervention exists.
