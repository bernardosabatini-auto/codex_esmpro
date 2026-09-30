# H200 inference profiling

Job 49346371 completed successfully in 14 minutes 35 seconds on one H200. Fifty real-checkpoint throughput/memory configurations were measured with Nsight Systems hardware counters. All eight cached/uncached coordinate checks matched exactly.

**Whole capture:** SM activity 70.0%; instruction issue 36.0%; tensor-pipeline activity 8.3%. SM activity includes warps waiting on memory and does not measure peak BF16 FLOPs.

Selected batches are the smallest within 95% of best measured throughput, with at least 50% SM activity and less than 85% reserved memory. Cached ESM embeddings are already resident; these measurements exclude ESMC and disk I/O.

| Model | Padded length | Batch | Proteins/s | SM active | Tensor active | Peak allocated GiB | Peak reserved GiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| pair-free | 128 | 128 | 32.32 | 93.9% | 14.6% | 13.6 | 15.0 |
| pair-free | 256 | 64 | 12.91 | 94.9% | 12.5% | 20.0 | 22.0 |
| pair-free | 384 | 64 | 7.28 | 96.9% | 11.7% | 42.6 | 47.1 |
| pair-free | 512 | 32 | 4.58 | 96.3% | 10.0% | 38.0 | 42.0 |
| pair | 128 | 128 | 28.80 | 94.4% | 13.8% | 13.6 | 15.0 |
| pair | 256 | 64 | 10.80 | 95.6% | 11.6% | 21.2 | 22.2 |
| pair | 384 | 32 | 5.64 | 95.4% | 9.9% | 23.5 | 24.6 |
| pair | 512 | 32 | 3.55 | 96.9% | 9.3% | 40.2 | 42.2 |

The next comparison uses two H200s, one per frozen checkpoint: 626 development targets × 3 samples × 3 flow step counts (10, 25, 50) × 2 guidance settings (1, 2), for 22,536 structures. Estimated inference sweep: 15–18 minutes per GPU plus startup, controls, transfers, and output. Budget 20–30 minutes each; hard limit 45 minutes. Each run checks real-weight batching equivalence before the full sweep. CPU scoring follows GPU release.

This is a development-set accuracy/cost comparison, not a new trained model, untouched test result, or end-to-end sequence-folding speed claim. The low tensor activity leaves substantial optimization work; kernel/stage profiling and controlled compilation are subsequent steps.

Comparison array **49349478** stopped at the batching controls before the full sweep. The pair and pair-free tasks ran for 3:17 and 3:19 respectively. Target 5eft_B differed by 0.430 and 0.641 Å RMSD between padded batch and unpadded single predictions (self CA lDDT 0.980 and 0.956); both exceeded the predeclared tolerance. Reference CA lDDT changed only 0.00013 and 0.00092, but the invariance failure still requires diagnosis. No larger-comparison results are claimed. Only these registered jobs were inspected or managed.
