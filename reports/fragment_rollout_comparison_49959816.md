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
    "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
    "d157e7e209ec5657817e94b993c9c66aab34328856000a6a40bcc38edd7df8cd"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.1015625,
      "candidate": 0.125,
      "candidate_minus_baseline": {
        "mean": 0.0234375,
        "ci95": [
          -0.0234375,
          0.0703125
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 6.111161314416677,
      "candidate": 5.426049778936431,
      "candidate_minus_baseline": {
        "mean": -0.685111535480246,
        "ci95": [
          -1.3017348102817778,
          -0.16912042007315903
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 1.0,
      "candidate_minus_baseline": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.0390625
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.39837219619411485,
      "candidate": 0.4132913293034659,
      "candidate_minus_baseline": {
        "mean": 0.014919133109351113,
        "ci95": [
          0.0021191266644319112,
          0.027368576373876276
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.015625,
      "candidate_minus_baseline": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 3.2622947208583355,
      "candidate": 3.0469422806054354,
      "candidate_minus_baseline": {
        "mean": -0.21535244025290012,
        "ci95": [
          -0.4275852418970317,
          -0.00913667376153174
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 1.0,
      "candidate_minus_baseline": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.2993857629656352,
      "candidate": 0.2964438786148118,
      "candidate_minus_baseline": {
        "mean": -0.0029418843508234385,
        "ci95": [
          -0.009945480260542698,
          0.004014325545398994
        ],
        "families": 16
      }
    }
  ]
}
```
