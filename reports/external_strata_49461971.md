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
