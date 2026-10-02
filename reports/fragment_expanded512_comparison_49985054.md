# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "reference_data_breadth",
  "matched_updates": 2000,
  "comparison_endpoint": 2000,
  "target_draws_matched": false,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
    "d5f2beac7d19ba5d16c76509a1b1b039a8db13523910d93da62ed086c3d16b68"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0703125,
      "candidate": 0.0703125,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
          0.0234375
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 5.778174917213619,
      "candidate": 5.654690294060856,
      "candidate_minus_baseline": {
        "mean": -0.12348462315276265,
        "ci95": [
          -0.32436382574960587,
          0.09343770333798591
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.9765625,
      "candidate": 1.0,
      "candidate_minus_baseline": {
        "mean": 0.0234375,
        "ci95": [
          0.0,
          0.046875
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.3637502026589584,
      "candidate": 0.360505610008572,
      "candidate_minus_baseline": {
        "mean": -0.0032445926503863734,
        "ci95": [
          -0.007143680839496129,
          0.0004843113770821677
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.046875,
      "candidate": 0.046875,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          -0.046875,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 2.3216553665697575,
      "candidate": 2.271076229400933,
      "candidate_minus_baseline": {
        "mean": -0.05057913716882467,
        "ci95": [
          -0.21517452830448747,
          0.09780303018633273
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
          -0.046875,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.31240692295216455,
      "candidate": 0.3130722571925958,
      "candidate_minus_baseline": {
        "mean": 0.0006653342404312618,
        "ci95": [
          -0.0047116747378490335,
          0.006190710675931408
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.171875,
      "candidate": 0.1953125,
      "candidate_minus_baseline": {
        "mean": 0.0234375,
        "ci95": [
          -0.0390625,
          0.0859375
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 4.376887863967568,
      "candidate": 4.251999533735216,
      "candidate_minus_baseline": {
        "mean": -0.12488833023235202,
        "ci95": [
          -0.456195391213987,
          0.23703225312056014
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
      "candidate": 0.3789949035823284,
      "candidate_minus_baseline": {
        "mean": -0.0017114223974159662,
        "ci95": [
          -0.0073165817444623945,
          0.003981316834235247
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
          0.1875
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 1.9615341303870082,
      "candidate": 1.7227803831920028,
      "candidate_minus_baseline": {
        "mean": -0.23875374719500542,
        "ci95": [
          -0.3717262702295557,
          -0.09937360617332161
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
      "candidate": 0.3284321717242533,
      "candidate_minus_baseline": {
        "mean": 0.003461438770562885,
        "ci95": [
          -0.003305918130469187,
          0.010509855627584178
        ],
        "families": 16
      }
    }
  ]
}
```
