# Restricted versus full-network balanced adaptation

Checkpoint 500; both seeds retained. Configurations, initial predictions, target/label/LR logs and frozen raw/EMA hashes verified. All cohorts are training data; biological diversity and generalization require separate evaluation.

| Seed / arm / cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|---:|
| 2026100171_full_all122 | 0.79403 | 0.64495 | 0.99283 | 0.92101 | 0.44419 |
| 2026100171_tail_all122 | 0.67965 | 0.40472 | 0.96798 | 0.86435 | 0.58314 |
| 2026100171_initial_all122 | 0.67562 | 0.41127 | 0.99206 | 0.86886 | 0.58185 |
| 2026100171_full_original32 | 0.75714 | 0.57381 | 0.99512 | 0.93988 | 0.44127 |
| 2026100171_tail_original32 | 0.71369 | 0.45342 | 0.96094 | 0.89341 | 0.52818 |
| 2026100171_initial_original32 | 0.74747 | 0.50446 | 0.99219 | 0.89842 | 0.51619 |
| 2026100171_full_additional90 | 0.80714 | 0.67024 | 0.99201 | 0.91430 | 0.44523 |
| 2026100171_tail_additional90 | 0.66755 | 0.38741 | 0.97049 | 0.85402 | 0.60268 |
| 2026100171_initial_additional90 | 0.65008 | 0.37813 | 0.99201 | 0.85835 | 0.60519 |
| 2026100181_full_all122 | 0.80796 | 0.65767 | 0.98924 | 0.92122 | 0.43549 |
| 2026100181_tail_all122 | 0.66221 | 0.39331 | 0.96875 | 0.86304 | 0.58294 |
| 2026100181_initial_all122 | 0.67562 | 0.41127 | 0.99206 | 0.86886 | 0.58185 |
| 2026100181_full_original32 | 0.82381 | 0.64226 | 0.99121 | 0.93723 | 0.42186 |
| 2026100181_tail_original32 | 0.73631 | 0.45342 | 0.96289 | 0.89167 | 0.52288 |
| 2026100181_initial_original32 | 0.74747 | 0.50446 | 0.99219 | 0.89842 | 0.51619 |
| 2026100181_full_additional90 | 0.80233 | 0.66315 | 0.98854 | 0.91552 | 0.44034 |
| 2026100181_tail_additional90 | 0.63586 | 0.37193 | 0.97083 | 0.85286 | 0.60430 |
| 2026100181_initial_additional90 | 0.65008 | 0.37813 | 0.99201 | 0.85835 | 0.60519 |

2026100171_tail_all122_vs_full: recall delta -0.11437, 95% interval [-0.16717408274785323, -0.06369901444184232]; validity delta -0.02485.

2026100171_tail_all122_vs_initial: recall delta +0.00403, 95% interval [-0.023663885636221703, 0.032280444964871174]; validity delta -0.02408.

2026100181_tail_all122_vs_full: recall delta -0.14576, 95% interval [-0.20068354800936766, -0.09325624512099923]; validity delta -0.02049.

2026100181_tail_all122_vs_initial: recall delta -0.01342, 95% interval [-0.03682718579234973, 0.009134465261514426]; validity delta -0.02331.
