# CUDA graph sampler probe

Status: complete; numerical/resource qualified: True.

Same compact balanced500 checkpoint, FP32 CFG1/Euler25/AE3;8 development families,3 paired noise repeats,K1/32. GPU-cached embeddings/noise to CPU backbone only. Graph capture/loading/ESMC/disk excluded. All replay copies, validation and cloning included. No full sequence-to-backbone speed claim.

| Samples | Eager s | Captured s | Ratio | Family95% interval |
|---|---:|---:|---:|---|
| 1 | 0.2837 | 0.2793 | 1.0154 | [1.0120923579526984, 1.020619081624839] |
| 32 | 3.5623 | 3.5568 | 1.0016 | [1.0008600702645452, 1.002279039147583] |

Peak reserved44.215GiB. Graph construction seconds by(bucket,K): [(128, 1, 0.638), (128, 32, 3.02), (256, 1, 0.667), (256, 32, 6.576), (384, 1, 0.953), (384, 32, 10.933), (512, 1, 1.246), (512, 32, 15.141)]

Separate full-pipeline follow-up justified: False.
