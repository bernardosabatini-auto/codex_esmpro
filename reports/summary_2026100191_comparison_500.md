# Matched pretrained ESM-summary learning feasibility

All32 families are training data; teacher-defined states are predictions, not biological populations.

Seed2026100191; initial predictions/weights and logged target/label/LR draws agree. Replication justified: False.

| Arm | Recall@32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | Balanced TV |
|---|---:|---:|---:|---:|---:|
| initial | 0.74747 | 0.99219 | 0.89842 | 0.88265 | 0.51619 |
| projected_final | 0.89390 | 0.99707 | 0.95949 | 0.92733 | 0.39623 |
| teacher_summary | 0.88943 | 0.99707 | 0.95980 | 0.92756 | 0.39135 |

Mixture versusinitial: recall difference+0.14196, paired family95% interval[0.03883184523809524, 0.2450967261904761]; validity difference+0.00488.

Mixture versusprojected_final: recall difference-0.00446, paired family95% interval[-0.03571428571428572, 0.026785714285714288]; validity difference+0.00000.

{'recall_gain': False, 'positive_recall_interval': False, 'validity_vs_control': True, 'validity_vs_initial': True}

No native/external promotion follows from this training result. Retain all arms, failures and locked-test quarantine.
