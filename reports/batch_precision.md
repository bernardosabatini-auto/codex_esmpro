# Batch precision diagnosis

Two single-H200 diagnostic jobs (49412468 and 49412705) separated flow precision, decoder precision, padding, and batch shape using identical per-target noise. The focused test used two targets, exact/padded singles, batches of 2, and batches of 64. These are numerical controls, not new folding-accuracy results.

| Model | Flow | Decoder | Worst batch RMSD (Å) | Minimum self CA lDDT | All controls pass |
|---|---|---|---:|---:|---|
| pair-free | bf16 | bf16 | 0.6408 | 0.9563 | False |
| pair-free | bf16 | fp32 | 0.6390 | 0.9560 | False |
| pair-free | fp16 | fp32 | 0.0738 | 1.0000 | True |
| pair-free | fp32 | bf16 | 0.0468 | 1.0000 | True |
| pair-free | fp32 | fp32 | 0.0074 | 1.0000 | True |
| pair-free | tf32 | fp32 | 0.0535 | 1.0000 | True |
| pair | bf16 | bf16 | 0.4299 | 0.9804 | False |
| pair | bf16 | fp32 | 0.4285 | 0.9807 | False |
| pair | fp16 | fp32 | 0.3511 | 0.9852 | False |
| pair | fp32 | bf16 | 0.0451 | 1.0000 | True |
| pair | fp32 | fp32 | 0.0067 | 1.0000 | True |
| pair | tf32 | fp32 | 0.0712 | 1.0000 | True |

The main discrepancy came from BF16 flow computation. Holding latent values fixed made decoder batching pass. Strict FP32 flow/decoder reduced the worst coordinate discrepancy below 0.008 Å, but flow inference took about three times longer in the tested large batch. FP16 failed for the pair model.

The selected policy keeps flow tensors in FP32 with PyTorch `float32_matmul_precision="high"` (labeled `tf32` in the configuration), and runs the decoder in IEEE FP32. At batch 64, length 256, the pair flow took 5.38 s versus 5.16 s for BF16; the pair-free flow took 4.18 s versus 4.14 s. These are focused timings, not a complete throughput profile. Worst batch discrepancies were 0.071 Å and 0.054 Å, with self CA lDDT 1.0.

The original thresholds remain: RMSD ≤0.2 Å, self CA lDDT ≥0.99, and absolute reference CA lDDT change ≤0.005. Comparison array 49413324 uses these thresholds at the actual production batch sizes, across all four length buckets, before collecting the 22,536 predictions. Fresh Nsight counters measure its utilization.

An external USalign executable was built from [pylelab/USalign commit 1fa25a9](https://github.com/pylelab/USalign/tree/1fa25a958fe3095900eba2ef9b48562bdc462251). With fixed residue correspondence (`-TMscore 1`), rigid-transform, shuffled-correspondence, and mirror controls scored 1.00000, 0.08171, and 0.31512 respectively. This supports CPU scoring with optimized, reference-normalized TM-score as well as CA lDDT. Missing original residue maps remain a limitation of the inherited data.

The broader production-batch controls in 49413324 subsequently failed on a 382-residue target: pair/pair-free RMSDs were 0.389/0.259 Å. Both jobs stopped before the sweep. The fast policy is therefore not validated across all length buckets. Job 49413883 extends the diagnosis to 382- and 510-residue targets, comparing high-precision float32 matmul and strict FP32. Thresholds have not been relaxed.
