# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "actual_rollout_motif_objective",
  "matched_updates": 500,
  "comparison_endpoint": 500,
  "target_draws_matched": true,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
    "6afbcdf16dba2613d5872d625bf7b8e83800a742ed852b05d05d21650a24be3a"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0703125,
      "candidate": 0.09375,
      "candidate_minus_baseline": {
        "mean": 0.0234375,
        "ci95": [
          -0.0078125,
          0.0703125
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 5.778174917213619,
      "candidate": 4.714055757503957,
      "candidate_minus_baseline": {
        "mean": -1.0641191597096622,
        "ci95": [
          -1.6701416629017332,
          -0.5579082043608653
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.9765625,
      "candidate": 0.9609375,
      "candidate_minus_baseline": {
        "mean": -0.015625,
        "ci95": [
          -0.0546875,
          0.0234375
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.3637502026589584,
      "candidate": 0.37190102697682487,
      "candidate_minus_baseline": {
        "mean": 0.008150824317866425,
        "ci95": [
          0.001524876091600992,
          0.014217487821314071
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.046875,
      "candidate": 0.078125,
      "candidate_minus_baseline": {
        "mean": 0.03125,
        "ci95": [
          -0.03125,
          0.09375
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 2.3216553665697575,
      "candidate": 2.0609835609793663,
      "candidate_minus_baseline": {
        "mean": -0.26067180559039116,
        "ci95": [
          -0.48607430572155863,
          -0.051935224584304086
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.984375,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.31240692295216455,
      "candidate": 0.3174837890974248,
      "candidate_minus_baseline": {
        "mean": 0.005076866145260244,
        "ci95": [
          -0.0022286176255718777,
          0.012134415286355957
        ],
        "families": 16
      }
    }
  ]
}
```
