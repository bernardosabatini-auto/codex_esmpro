# Guidance surrogate audit

Retrospective, repeatedly used four-family training diagnostic. Likelihood is an optimized surrogate, not independent designability evidence. No new sequence attempts, changed gates, or training labels.

| Arm | Mean motif NLL | Raw matches | Strict refold success | Designable |
|---|---:|---:|---:|---:|
| baseline | 3.142 | 3/16 | 1/16 | 4/16 |
| geometry | 3.173 | 15/16 | 0/16 | 4/16 |
| guided | 2.501 | 10/16 | 0/16 | 5/16 |

Joint guidance reduced motif NLL in 16/16 paired samples. Lower is better for NLL. Strict success requires the same valid refold to match the original motif, global fold, and scaffold; all failures remain in the denominator.

The accompanying local JSON also reports chain and motif covalent-bond distributions (1st, 50th, 99th percentiles). These are descriptive, pooled-residue diagnostics, not a stereochemical validation or a new gate.

One RTX; 435.2 worker seconds; 30.36/95.59 GiB peak/total device memory. 128 new sequence refolds; 160 unchanged baseline/native attempts reused.

Captured weighted utilization: 41.18% over 427 complete one-second samples. SM 72.78%, tensor 0.41%, DRAM 36.62%, graphics engine 82.39%. Excludes pre-recorder startup; not the dashboard 24-hour statistic. Device memory occupancy is distinct from DRAM activity.
