# Cached-frame supervision and shorter sampling

Status: experiments in progress. No model promoted and no confirmation or independent-test targets scored.

## Rotation finding and correction

ProteinAE codes change strongly under a rigid rotation of an otherwise identical structure. The inherited dataset already handled orientation with PCA canonicalization; the earlier interpretation overlooked that preprocessing. Fresh raw-file labels and first-residue-frame labels both changed the inherited convention. See the [corrected rotation verdict](rotation_verdict_20261001.md).

The new labels preserve every cached reference latent bit-for-bit and align each teacher conformation to the cached reference coordinates with one proper global transform. All 512 reference identities and all 8,192 teacher round trips passed. Reconstruction mean CA-lDDT is 0.999408 and decoded coarse validity is 0.991455 versus 0.995728 at input. Internal geometry and chirality are preserved by alignment. Reference structures are used for training labels only.

Independent PCA applied to each already reference-aligned teacher conformation introduces an extra frame change greater than 90° in 39.5% of samples, including 17.0% of samples within 1 Å aligned-core RMSD of the reference. This motivates a common ensemble frame; it does not establish an accuracy benefit or remove frame discontinuities between different sequences.

## Matched cached-frame training

Jobs 49654680 and 49654703 use identical initialization, seed, target batches, optimizer schedule and 2,000-update budget. The only configuration difference is reference-only versus 50% reference / 50% valid aligned empirical teacher labels. The matched-run audit passed through 500 updates. Each job uses one H200 with a 100-minute limit.

At 500 updates on 64 tuning families with three samples each:

| Arm | CA-lDDT | Change from initialization | 95% family interval |
|---|---:|---:|---|
| Cached reference | 0.77857 | −0.00526 | [−0.00832, −0.00245] |
| Cached reference plus aligned teacher | 0.78729 | +0.00345 | [−0.00131, +0.00807] |

Aligned teacher supervision exceeds the matched reference control by 0.00871 [0.00433, 0.01315], but improvement over initialization remains uncertain. Validity does not improve. These are development results from one training seed and AFDB predicted references, not an independent accuracy claim. Full [500-update results](cached_frame_training_500.md) include validity and the Kabsch-based TM diagnostic; optimized fixed-correspondence TM will be reported separately.

Both predeclared checkpoints receive frozen 48-protein ensemble evaluation. The 500-update jobs are 49660833 and 49660888. The 500-update ensemble scores are complete:

| Model | State coverage at 32 | Nearest-reference CA-lDDT | Coarse validity | MD W1 (lower is better) |
|---|---:|---:|---:|---:|
| Inherited baseline | 0.43750 | 0.86794 | 0.99414 | 0.48850 |
| Cached reference, 500 | 0.46875 | 0.86266 | 0.98763 | 0.48682 |
| Aligned teacher, 500 | 0.46875 | 0.86631 | 0.99284 | 0.47598 |

Teacher versus reference-only state coverage is identical for every family. Teacher-supervised MD W1 is lower by 0.01084 [0.00178, 0.02192], a secondary distributional improvement, with 11 of 16 families improving versus the control and 14 of 16 versus initialization; nearest-reference quality is higher by 0.00365 [0.00128, 0.00634]. Relative to initialization, teacher-supervised quality decreases by 0.00163 but stays within the 0.005 margin. Neither arm passes the primary training-diversity promotion gate. See comparisons against [baseline](cached_aligned_500_vs_baseline.md) and [matched control](cached_aligned_500_vs_reference.md). Final-checkpoint jobs have registered, deduplicated timer follow-ups. Completion scoring is automatic; the watcher does not resume conversation reasoning.

## Separate shorter-sampler experiment

The inherited 25-step CFG2 student supplies 16 recorded Gaussian-seed/latent-endpoint pairs for each of the same 512 training families. These labels preserve the existing student distribution; they add no biological-state supervision. Paired-noise reflow is compared with fresh independent noise on identical endpoint draws. The approach follows the straight-path coupling objective of [rectified flow](https://arxiv.org/abs/2209.03003); its success on these protein latents is an experimental question. Both arms use the same initialization, data order, time/dropout random streams, 2,000 updates and CFG1 inference. Evaluate 5 and 10 steps at 500 and 2,000 updates.

Data jobs: 49655628, 49657893, 49658005 and 49658117. The first shard passed all four length-bucket batching controls, using 15.2 GiB peak reserved memory. Measured SM issue was 56.0% over the full capture and 69.6% during sampling. The 40-update training profile, 49657719, passed at 65.0 GiB: 59.7% SM issue during training, 33.2% over its short capture including startup. Full-run utilization remains to be measured. The other two shards with valid counter coverage measured 57.7% and 56.3% whole-capture SM issue. Shard 49657893 had incomplete counter coverage and supplies no utilization estimate.

All 8,192 pairs are complete. Full paired and independent training jobs are 49662855 and 49662912, each one H200 with a 100-minute limit; final 5/10-step ensemble follow-ups are predeclared in the guarded timer.

Preserved decoded quality and valid-state coverage must accompany at least a twofold measured K=32 speedup over the inherited student before a sampler can qualify. Timing includes sequence embedding and decoding on the same GPU, with the direct teacher reported too. Fewer steps alone are not evidence of useful speed.

All GPU submissions use exact project job registration, immutable code/configuration snapshots, completion handlers and an eight-GPU running-plus-pending cap. Data, weights and raw results remain excluded from Git.

Documentation clarification: the frozen cached-frame protocol retained the phrase “raw reference” in its distribution description. Its operative reference-label rule, generated configurations, bitwise audit and executed code all use inherited cached reference latents; raw-file latents are not used in either new arm. The frozen protocol was not rewritten after execution.

## Short-sampler 500-update screen

All four 500-update short samplers fail native validity. Paired 10-step CA-lDDT is 0.79019 versus initialization 0.78384, but validity falls from 0.97917 to 0.94792. Independent 10-step validity is 0.92188. Five-step validity is 0.77083 (paired) and 0.61458 (independent). See [the full tuning comparison](reflow_training_500.md).

Resource decision, made before 2,000-update outcomes: skip ensemble generation for these failed 500-update samplers. Both training arms still complete the planned budget and both final sampler settings receive full native evaluation. Final ensemble submissions now require the same existing native noninferiority and validity margins (CA-lDDT lower 95% family bound above −0.005; mean validity loss no greater than 0.01). This refines the initially broad ensemble follow-up plan to avoid spending GPU time on candidates that cannot qualify. The guarded timer records every failed screen instead of silently retrying or discarding it. Cached-frame 500/2,000 ensemble comparisons remain unchanged.

## Final cached-frame native evaluation

Both 2,000-update runs are complete. Aligned teacher CA-lDDT is 0.78758, a change of +0.00374 [−0.00078, +0.00885] from initialization and +0.00984 [0.00600, 0.01385] from the matched reference control. Optimized fixed-correspondence TM is 0.68753 versus 0.68488 initially, a change of +0.00266 [−0.00316, +0.00876]. Native coarse validity falls from 0.97917 to 0.95833. These results do not establish an accuracy gain over initialization.

Final ensemble jobs 49672152 and 49672377 are queued. Their requested limits were reduced, for these own jobs only, from 30 minutes/96 GiB host RAM to 15 minutes/16 GiB after the matching 500-update jobs completed in 7m13s and 7m18s with approximately 2.6 GiB host RSS. Scheduler adjustment records are retained locally. GPU memory limits and numerical settings are unchanged.

The reference-control training run measured 58.05% allocation-normalized SM issue, 60.39% during training, and 63.65 GiB peak GPU memory. The aligned-teacher run's counter coverage failed validation, so no utilization figure is assigned to that run. See [allocation accounting](cached_frame_gpu_allocation.md).
