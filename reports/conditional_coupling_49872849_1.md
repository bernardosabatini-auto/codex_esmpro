# Small-ensemble learnability diagnostic

Status: complete; arm: aligned_teacher; profile only: False.

32 training proteins selected for teacher diversity. Teacher-defined contact modes are predictions, not measured biological states. Fresh32-sample ensembles at CFG1; all samples retained. Coverage requires feature RMSE<=2A, nearest-contact teacher CA-lDDT>=0.8 and coarse-valid geometry.

| Updates / guidance | Mode recall @32 | Coarse valid | Teacher CA-lDDT | Reference CA-lDDT | State TV (lower better) |
|---|---:|---:|---:|---:|---:|
| 0_cfg1 | 0.74821 | 0.98828 | 0.89806 | 0.88196 | 0.53027 |
| 500_cfg1 | 0.87738 | 0.99219 | 0.95681 | 0.92527 | 0.36328 |

Training label distribution: balanced. The state-TV column always compares with the original empirical teacher prior; equal-state-prior TV is reported separately by analyze_overfit_states.py.

Latent diagnostics (nearest teacher RMSE): global reference fits below are evaluation-only and never alter predictions.

| Updates / guidance | Sampled latent | Re-encoded backbone | Pose-aligned re-encoded backbone | Decoder/encoder RMSE |
|---|---:|---:|---:|---:|
| 0_cfg1 | 0.44001 | 0.44041 | 0.13697 | 0.00565 |
| 500_cfg1 | 0.35197 | 0.35235 | 0.07106 | 0.00582 |

Training: 1158.83 seconds; peak reserved memory: 64.62 GiB.

Processed 8000 protein examples and 1920000 padded residue examples: 6.90 examples/s and 1656.84 padded residues/s. Compare batch/length distributions before interpreting throughput differences.

This is a training-capacity experiment. No model promotion or unseen-family accuracy claim is possible from these scores.

Within-sequence coupling audit:
{
  "complete_updates": 500,
  "arm": "optimal",
  "groups": 1000,
  "mean_independent_cost": 2.000585830748509,
  "mean_optimal_cost": 1.99624926864735,
  "mean_applied_cost": 1.99624926864735
}

Contiguous groups of8same-protein examples; target marginals preserved exactly. Compare only matched grouping/noise recipes; lower transport or training loss is not evidence of improved structural diversity.
