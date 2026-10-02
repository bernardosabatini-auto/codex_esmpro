# Fixed-latent decoder integration comparison

Status: complete.

Five pipelines,64 tuning families,three paired samples. Latents and decoder noise held fixed across3/5/10 steps. All source3-step scores and backbones must reproduce. Strict FP32, all samples retained; no locked-test scoring. Unadjusted family intervals. Component costs exclude ESMC, loading and untimed warmups and are not end-to-end benchmarks.

| Head / decoder | CA-lDDT | CA delta vs original3 |95% interval | Valid | Validity delta | Qualified | Flow s | Decoder s |
|---|---:|---:|---|---:|---:|---|---:|---:|
| original_decoder3 | 0.78384 | +0.00000 | [0.0, 0.0] | 0.97917 | +0.00000 | True | 70.87 | 4.20 |
| original_decoder5 | 0.78444 | +0.00060 | [0.0004128460064978425, 0.0007918669373743195] | 0.97917 | +0.00000 | True | 70.87 | 6.98 |
| original_decoder10 | 0.78452 | +0.00069 | [0.0003736054997947126, 0.0010079336413308887] | 0.97917 | +0.00000 | True | 70.87 | 13.96 |
| seed2026100171_empirical_decoder3 | 0.79288 | +0.00904 | [0.0051314770177791815, 0.01319946506437796] | 0.96354 | -0.01562 | False | 36.06 | 4.20 |
| seed2026100171_empirical_decoder5 | 0.79334 | +0.00950 | [0.005545649018602197, 0.013669974360826093] | 0.96354 | -0.01562 | False | 36.06 | 6.98 |
| seed2026100171_empirical_decoder10 | 0.79337 | +0.00953 | [0.0055685955244769774, 0.013704518263063506] | 0.96875 | -0.01042 | False | 36.06 | 13.96 |
| seed2026100171_balanced_decoder3 | 0.78794 | +0.00410 | [-0.001569854335074207, 0.00901624221794908] | 0.95312 | -0.02604 | False | 36.08 | 4.20 |
| seed2026100171_balanced_decoder5 | 0.78842 | +0.00458 | [-0.001082187969012436, 0.009492354162208408] | 0.94792 | -0.03125 | False | 36.08 | 6.98 |
| seed2026100171_balanced_decoder10 | 0.78839 | +0.00455 | [-0.0011436815386265317, 0.00949959675571951] | 0.94792 | -0.03125 | False | 36.08 | 13.96 |
| seed2026100181_empirical_decoder3 | 0.78693 | +0.00309 | [-0.004399154761459621, 0.009143243047777808] | 0.95833 | -0.02083 | False | 36.03 | 4.19 |
| seed2026100181_empirical_decoder5 | 0.78741 | +0.00358 | [-0.003950109794631966, 0.009671263800926302] | 0.95833 | -0.02083 | False | 36.03 | 6.98 |
| seed2026100181_empirical_decoder10 | 0.78741 | +0.00357 | [-0.003972952951932123, 0.009652180410817595] | 0.95833 | -0.02083 | False | 36.03 | 13.96 |
| seed2026100181_balanced_decoder3 | 0.78827 | +0.00443 | [-0.001620546576334707, 0.009320844237129722] | 0.96354 | -0.01562 | False | 36.07 | 4.20 |
| seed2026100181_balanced_decoder5 | 0.78875 | +0.00491 | [-0.001180376769637323, 0.009797150446267612] | 0.96875 | -0.01042 | False | 36.07 | 6.98 |
| seed2026100181_balanced_decoder10 | 0.78871 | +0.00487 | [-0.0012151633188755716, 0.009749965373941719] | 0.96875 | -0.01042 | False | 36.07 | 13.95 |

| Within-head change from decoder3 | CA-lDDT difference | Validity difference | Clash-fraction difference | Peptide-outlier difference |
|---|---:|---:|---:|---:|
| original_decoder3 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| original_decoder5 | +0.00060 | +0.00000 | -0.00011 | -0.00103 |
| original_decoder10 | +0.00069 | +0.00000 | -0.00008 | -0.00139 |
| seed2026100171_empirical_decoder3 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| seed2026100171_empirical_decoder5 | +0.00046 | +0.00000 | -0.00001 | -0.00119 |
| seed2026100171_empirical_decoder10 | +0.00049 | +0.00521 | +0.00001 | -0.00151 |
| seed2026100171_balanced_decoder3 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| seed2026100171_balanced_decoder5 | +0.00048 | -0.00521 | -0.00000 | -0.00122 |
| seed2026100171_balanced_decoder10 | +0.00045 | -0.00521 | +0.00003 | -0.00156 |
| seed2026100181_empirical_decoder3 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| seed2026100181_empirical_decoder5 | +0.00049 | +0.00000 | -0.00004 | -0.00101 |
| seed2026100181_empirical_decoder10 | +0.00048 | +0.00000 | +0.00002 | -0.00122 |
| seed2026100181_balanced_decoder3 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| seed2026100181_balanced_decoder5 | +0.00048 | +0.00521 | -0.00010 | -0.00113 |
| seed2026100181_balanced_decoder10 | +0.00044 | +0.00521 | -0.00008 | -0.00130 |

Both balanced seeds qualify by decoder length: {'3': False, '5': False, '10': False}.
Geometry recovery is not proof of improved biological diversity. Separate ensembles and matched sequence timing remain necessary.
