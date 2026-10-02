# Original versus anchored reconstruction calibration

```json
{
  "status": "complete",
  "manifest_sha256": "705beaca500467b60091978dc38a24fd6834ed203fad8413041eaee42fe3a0fb",
  "paired_cases": 288,
  "training_families": 32,
  "summary": {
    "original": {
      "coarse_valid": 288,
      "valid_global_under_half_A": 267,
      "valid_motif_under_one_A": 285,
      "mean_global_rmsd": 0.21287395306462528,
      "mean_motif_rmsd": 0.1467832635166787
    },
    "anchored": {
      "coarse_valid": 288,
      "valid_global_under_half_A": 267,
      "valid_motif_under_one_A": 286,
      "mean_global_rmsd": 0.20660092948218642,
      "mean_motif_rmsd": 0.14403952328606845
    }
  },
  "anchored_minus_original": {
    "global_rmsd": {
      "mean": -0.006273023582438866,
      "ci95": [
        -0.019521814365125956,
        0.005526518369022437
      ],
      "families": 32
    },
    "motif_rmsd": {
      "mean": -0.0027437402306102407,
      "ci95": [
        -0.01995775911792276,
        0.010101101322739333
      ],
      "families": 32
    }
  },
  "original_data_gate_passed": false,
  "interpretation": "Diagnostic only; original failed gate preserved; no training authorized by this report",
  "elapsed_seconds": 55.90105302585289
}
```
