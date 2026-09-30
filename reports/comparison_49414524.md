# Frozen-head comparison

All targets and samples are retained; no best-of-three selection. Fixed residue correspondence TM-score (USalign -TMscore 1) and CA lDDT. Timings cover cached embeddings to coordinates, including transfers; ESMC extraction is excluded.

These are separately trained legacy checkpoints. Their difference does not isolate the causal effect of adding a pair track.

| Model | Steps / guidance | Mean TM | CA lDDT | Predictions/s | Allocated / reserved GiB |
|---|---|---:|---:|---:|---:|
| pair | steps10_cfg1 | 0.53831 | 0.65136 | 12.08 | 58.2 / 58.3 |
| pair | steps10_cfg2 | 0.56324 | 0.66282 | 7.90 | 58.2 / 58.3 |
| pair | steps25_cfg1 | 0.54685 | 0.65780 | 6.77 | 58.2 / 58.3 |
| pair | steps25_cfg2 | 0.56824 | 0.67450 | 3.90 | 58.2 / 58.3 |
| pair | steps50_cfg1 | 0.55002 | 0.65962 | 3.91 | 58.2 / 58.3 |
| pair | steps50_cfg2 | 0.56841 | 0.67705 | 2.12 | 58.2 / 58.3 |
| pair_free | steps10_cfg1 | 0.53086 | 0.64107 | 17.73 | 47.1 / 51.7 |
| pair_free | steps10_cfg2 | 0.55561 | 0.65598 | 10.22 | 47.1 / 51.7 |
| pair_free | steps25_cfg1 | 0.53692 | 0.64818 | 8.43 | 47.1 / 51.7 |
| pair_free | steps25_cfg2 | 0.55934 | 0.66709 | 4.49 | 47.1 / 51.7 |
| pair_free | steps50_cfg1 | 0.54023 | 0.65019 | 4.49 | 47.1 / 51.7 |
| pair_free | steps50_cfg2 | 0.55955 | 0.66844 | 2.32 | 47.1 / 51.7 |

## Paired results

95% paired target-bootstrap CI after averaging three samples per target; no homology clusters available; exploratory development-set comparisons.

| Setting | Pair minus pair-free TM | 95% CI |
|---|---:|---|
| steps10_cfg1 | 0.00745 | [0.00391, 0.01086] |
| steps10_cfg2 | 0.00762 | [0.00484, 0.01051] |
| steps25_cfg1 | 0.00993 | [0.00688, 0.01289] |
| steps25_cfg2 | 0.00890 | [0.00609, 0.01174] |
| steps50_cfg1 | 0.00979 | [0.00735, 0.01226] |
| steps50_cfg2 | 0.00886 | [0.00601, 0.01169] |

pair: going from 25 to 50 steps at guidance 2 changes mean TM by 0.00017 (95% CI [-0.00097, 0.00134]).

pair_free: going from 25 to 50 steps at guidance 2 changes mean TM by 0.00021 (95% CI [-0.00093, 0.00137]).

## Hardware counters

SM activity includes waiting warps and is not percent of peak FLOPs. Instruction issue and tensor activity are reported separately. Strict FP32 is the correctness reference; these results do not establish efficient BF16 inference.

| Model | Scope | SM active % | SM issue % | Tensor active % |
|---|---|---:|---:|---:|
| pair | whole_capture_mean_percent | 91.3 | 71.4 | 1.1 |
| pair | collection_mean_percent | 96.4 | 75.5 | 1.1 |
| pair_free | whole_capture_mean_percent | 89.9 | 72.6 | 1.0 |
| pair_free | collection_mean_percent | 96.3 | 77.8 | 1.1 |

## Interpretation and next work

Choose sampling settings using this development set, then freeze them for a separate test set. More sampling steps are useful only if their accuracy gain justifies measured cost. Compare checkpoint quality separately from architectural causality: a controlled training ablation remains required.

The next efficiency experiment should preserve this FP32 reference while testing which operations need higher precision. Missing original residue maps and sequence-homology controls remain unresolved dataset limitations. Do not compare these fixed-correspondence scores directly with the earlier report without auditing its alignment protocol.
