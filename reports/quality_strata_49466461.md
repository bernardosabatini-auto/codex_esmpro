# Development accuracy diagnostics

Exploratory strata; no multiplicity correction and no change to the primary promotion gate. All inference samples are averaged per target; pilot results also average the three training seeds. These confidence intervals are conditional on those seeds.

Reference CA breaks are a coordinate proxy, not verified residue maps or domain labels.

| Comparison (second minus first) | Stratum | Targets | Mean TM change | 95% sequence-cluster CI |
|---|---|---:|---:|---|
| esmfold2_fast_minus_untouched_pair | all | 626 | +0.03153 | [+0.02473, +0.03854] |
| esmfold2_fast_minus_untouched_pair | length_1_128 | 252 | +0.01469 | [+0.00277, +0.02689] |
| esmfold2_fast_minus_untouched_pair | length_129_256 | 207 | +0.03754 | [+0.02782, +0.04908] |
| esmfold2_fast_minus_untouched_pair | length_257_384 | 129 | +0.04795 | [+0.03394, +0.06366] |
| esmfold2_fast_minus_untouched_pair | length_385_512 | 38 | +0.05475 | [+0.03515, +0.07779] |
| esmfold2_fast_minus_untouched_pair | reference_CA_continuous | 412 | +0.02775 | [+0.01872, +0.03728] |
| esmfold2_fast_minus_untouched_pair | reference_CA_breaks | 214 | +0.03881 | [+0.02874, +0.04914] |
| confidence_minus_untouched_pair | all | 626 | -0.00217 | [-0.00311, -0.00121] |
| confidence_minus_untouched_pair | length_1_128 | 252 | -0.00249 | [-0.00415, -0.00072] |
| confidence_minus_untouched_pair | length_129_256 | 207 | -0.00152 | [-0.00313, +0.00001] |
| confidence_minus_untouched_pair | length_257_384 | 129 | -0.00250 | [-0.00439, -0.00058] |
| confidence_minus_untouched_pair | length_385_512 | 38 | -0.00247 | [-0.00474, -0.00041] |
| confidence_minus_untouched_pair | reference_CA_continuous | 412 | -0.00199 | [-0.00317, -0.00081] |
| confidence_minus_untouched_pair | reference_CA_breaks | 214 | -0.00252 | [-0.00410, -0.00088] |
| flow_minus_untouched_pair | all | 626 | -0.00248 | [-0.00346, -0.00147] |
| flow_minus_untouched_pair | length_1_128 | 252 | -0.00292 | [-0.00470, -0.00103] |
| flow_minus_untouched_pair | length_129_256 | 207 | -0.00164 | [-0.00316, -0.00013] |
| flow_minus_untouched_pair | length_257_384 | 129 | -0.00287 | [-0.00474, -0.00087] |
| flow_minus_untouched_pair | length_385_512 | 38 | -0.00279 | [-0.00542, -0.00047] |
| flow_minus_untouched_pair | reference_CA_continuous | 412 | -0.00209 | [-0.00333, -0.00083] |
| flow_minus_untouched_pair | reference_CA_breaks | 214 | -0.00323 | [-0.00480, -0.00164] |
| confidence_minus_flow | all | 626 | +0.00031 | [-0.00011, +0.00074] |
| confidence_minus_flow | length_1_128 | 252 | +0.00043 | [-0.00028, +0.00119] |
| confidence_minus_flow | length_129_256 | 207 | +0.00012 | [-0.00049, +0.00072] |
| confidence_minus_flow | length_257_384 | 129 | +0.00037 | [-0.00062, +0.00135] |
| confidence_minus_flow | length_385_512 | 38 | +0.00032 | [-0.00059, +0.00127] |
| confidence_minus_flow | reference_CA_continuous | 412 | +0.00010 | [-0.00037, +0.00058] |
| confidence_minus_flow | reference_CA_breaks | 214 | +0.00071 | [-0.00008, +0.00154] |
