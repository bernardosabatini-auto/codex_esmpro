# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "conditional_latent_motif_weight",
  "matched_updates": 2000,
  "comparison_endpoint": 2000,
  "target_draws_matched": true,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
    "6e2a7aa446e6ccbd7bd02d1c02de7f741c8ab9a4c6c222e35d0dc0042a2b6285"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0703125,
      "candidate": 0.0859375,
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
      "metric": "motif_drms",
      "baseline": 5.778174917213619,
      "candidate": 5.197461016708985,
      "candidate_minus_baseline": {
        "mean": -0.5807139005046338,
        "ci95": [
          -0.837731807155069,
          -0.37210399002069616
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.9765625,
      "candidate": 0.9921875,
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
      "baseline": 0.3637502026589584,
      "candidate": 0.3747627589481809,
      "candidate_minus_baseline": {
        "mean": 0.011012556289222476,
        "ci95": [
          0.00789971360685127,
          0.014495912266326303
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
          0.0,
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
      "candidate": 2.113869053311646,
      "candidate_minus_baseline": {
        "mean": -0.20778631325811148,
        "ci95": [
          -0.3794320120709017,
          -0.06728224197868257
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
      "candidate": 0.32189703685121757,
      "candidate_minus_baseline": {
        "mean": 0.00949011389905308,
        "ci95": [
          0.005421776350529924,
          0.013934692822675437
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.171875,
      "candidate": 0.265625,
      "candidate_minus_baseline": {
        "mean": 0.09375,
        "ci95": [
          0.03125,
          0.1640625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 4.376887863967568,
      "candidate": 3.7471692396793514,
      "candidate_minus_baseline": {
        "mean": -0.6297186242882162,
        "ci95": [
          -0.866227587533649,
          -0.42035126986447724
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.9921875,
      "candidate": 1.0,
      "candidate_minus_baseline": {
        "mean": 0.0078125,
        "ci95": [
          0.0,
          0.0234375
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.3807063259797444,
      "candidate": 0.3928150711602513,
      "candidate_minus_baseline": {
        "mean": 0.012108745180506881,
        "ci95": [
          0.0067382857660769156,
          0.017550164436567515
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.140625,
      "candidate": 0.234375,
      "candidate_minus_baseline": {
        "mean": 0.09375,
        "ci95": [
          0.0,
          0.203125
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 1.9615341303870082,
      "candidate": 1.641208268236369,
      "candidate_minus_baseline": {
        "mean": -0.3203258621506393,
        "ci95": [
          -0.5796662836917675,
          -0.12760735746705923
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 1.0,
      "candidate": 0.984375,
      "candidate_minus_baseline": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.3249707329536904,
      "candidate": 0.3356757846944973,
      "candidate_minus_baseline": {
        "mean": 0.010705051740806971,
        "ci95": [
          0.0026504350366432753,
          0.018766607799082798
        ],
        "families": 16
      }
    }
  ]
}
```
