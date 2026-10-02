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
    "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
    "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.1015625,
      "candidate": 0.0703125,
      "candidate_minus_baseline": {
        "mean": -0.03125,
        "ci95": [
          -0.078125,
          0.0078125
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 6.111161314416677,
      "candidate": 5.778174917213619,
      "candidate_minus_baseline": {
        "mean": -0.332986397203058,
        "ci95": [
          -0.7979048574052285,
          0.09310347076388985
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.9765625,
      "candidate_minus_baseline": {
        "mean": -0.0078125,
        "ci95": [
          -0.0390625,
          0.0234375
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.39837219619411485,
      "candidate": 0.3637502026589584,
      "candidate_minus_baseline": {
        "mean": -0.0346219935351564,
        "ci95": [
          -0.06799266910085486,
          -0.006077099524900714
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.046875,
      "candidate_minus_baseline": {
        "mean": 0.046875,
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
      "baseline": 3.2622947208583355,
      "candidate": 2.3216553665697575,
      "candidate_minus_baseline": {
        "mean": -0.940639354288578,
        "ci95": [
          -1.2827014717971905,
          -0.6197588932467625
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
      "baseline": 0.2993857629656352,
      "candidate": 0.31240692295216455,
      "candidate_minus_baseline": {
        "mean": 0.013021159986529345,
        "ci95": [
          0.0011834015702443807,
          0.024772498318533964
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.1953125,
      "candidate": 0.171875,
      "candidate_minus_baseline": {
        "mean": -0.0234375,
        "ci95": [
          -0.109375,
          0.0625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 5.782612983719446,
      "candidate": 4.376887863967568,
      "candidate_minus_baseline": {
        "mean": -1.405725119751878,
        "ci95": [
          -2.1591523956973107,
          -0.7455065313348318
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.9921875,
      "candidate_minus_baseline": {
        "mean": 0.0078125,
        "ci95": [
          -0.015625,
          0.03125
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.4661980832629693,
      "candidate": 0.3807063259797444,
      "candidate_minus_baseline": {
        "mean": -0.08549175728322488,
        "ci95": [
          -0.14031688265512768,
          -0.036852347529573566
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.140625,
      "candidate_minus_baseline": {
        "mean": 0.140625,
        "ci95": [
          0.03125,
          0.265625
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 3.3866354674100876,
      "candidate": 1.9615341303870082,
      "candidate_minus_baseline": {
        "mean": -1.4251013370230794,
        "ci95": [
          -1.735037022898905,
          -1.1119325366104023
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 1.0,
      "candidate": 1.0,
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
      "step": 2000,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.2970377822582705,
      "candidate": 0.3249707329536904,
      "candidate_minus_baseline": {
        "mean": 0.027932950695419918,
        "ci95": [
          0.013557835538343058,
          0.04255942848106227
        ],
        "families": 16
      }
    }
  ]
}
```
