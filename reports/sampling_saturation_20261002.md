# Sampling saturation on frozen experimental states

All16 eligible development families, unchanged contact-state definitions, valid2A hits and fixed sample prefixes. No sample filtering, state redefinition, or independent-test scoring. These conditional prefix curves do not measure equilibrium populations.

| Pipeline | K1 | K4 | K16 | K32 | K128 |
|---|---:|---:|---:|---:|---:|
| original | 0.28125 | 0.34375 | 0.43750 | 0.43750 | not run |
| candidate | 0.18750 | 0.31250 | 0.43750 | 0.43750 | not run |
| teacher | 0.25000 | 0.46875 | 0.53125 | 0.59375 | not run |
| teacher128 | 0.25000 | 0.46875 | 0.53125 | 0.59375 | 0.71875 |

original 16_to_32: coverage increment +0.00000, unadjusted paired-family95% interval [0.0, 0.0].

candidate 16_to_32: coverage increment +0.00000, unadjusted paired-family95% interval [0.0, 0.0].

teacher 16_to_32: coverage increment +0.06250, unadjusted paired-family95% interval [0.0, 0.15625].

teacher128 32_to_128: coverage increment +0.12500, unadjusted paired-family95% interval [0.03125, 0.21875].

The original and candidate students gain no additional observed states between16 and32 samples in these prefixes, while the teacher continues gaining through128. This supports prioritizing changes to the student distribution over a blind student sample-count expansion. Zero observed prefix gain does not prove that larger student ensembles can never reach additional states.

Do not divide these16-family coverage means by the latency benchmark’s different eight-sequence mean; a coverage-per-time comparison requires matched targets and budgets.

Sources: original: runs/state_scores_49618816/score.json, candidate: runs/state_scores_49771176/score.json, teacher: runs/state_scores_49626078/score.json, teacher128: runs/state_scores_49629888/score.json
