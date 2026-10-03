# Diversity of compatible cached teacher states

Descriptive CPU-only diagnostic on training proteins. All pairs of states that passed unchanged original0.5Afragment and0.8confidence eligibility. Proper-RMSD metrics use fixed residue correspondence. The1Adiversity count is descriptive, not a qualification gate or designability measure. Original broad-coverage failure is unchanged; no target replacement or model training follows automatically.

```json
{
  "all512": {
    "conditions": 4608,
    "eligible_conditions": 1376,
    "multiple_state_conditions": 1237,
    "median_max_scaffold_rmsd": 3.5906371260221097,
    "conditions_with_scaffold_pair_over_1A": 994,
    "proteins_with_scaffold_pair_over_1A": 321
  },
  "current128": {
    "conditions": 1152,
    "eligible_conditions": 474,
    "multiple_state_conditions": 428,
    "median_max_scaffold_rmsd": 2.3112012174971204,
    "conditions_with_scaffold_pair_over_1A": 322,
    "proteins_with_scaffold_pair_over_1A": 89
  }
}
```
