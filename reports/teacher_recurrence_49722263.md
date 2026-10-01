# Fresh teacher-state recurrence

Status: complete.

Both conditions use fresh matched diffusion seeds. Fixed trunk reuses the original stochastic teacher trunk; new trunk changes it. The original training atlas stays frozen. Atlas misses can indicate an incomplete atlas or poor structure and are not automatically invalid biological conformations. Singleton recurrence here uses fresh teacher generation; the earlier87.3% reference only resampled the16 stored teacher labels.

| Condition | Recall @2A | Recall @1A | Coarse valid | Atlas hit fraction | Teacher CA-lDDT | Empirical state TV | Singleton states hit |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_trunk | 0.83661 | 0.74301 | 1.00000 | 0.97949 | 0.98783 | 0.12695 | 32/51 |
| new_trunk | 0.85119 | 0.75759 | 1.00000 | 0.98145 | 0.98762 | 0.12402 | 33/51 |

Maximum CA RMSD in original-label reproduction: 0.000144 A; sampler replay: 0.000169 A. Peak reserved memory: 77.61 GiB.

Teacher predictions do not establish biological populations. One new trunk realization is a limited sensitivity check. No training examples or states are removed based on these outcomes.
