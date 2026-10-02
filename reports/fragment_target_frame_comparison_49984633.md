# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "conditional_target_frame",
  "matched_updates": 500,
  "comparison_endpoint": 500,
  "target_draws_matched": true,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
    "c51d7da4bb8b86ad6691706ba56f5b14599c0a3db1ffaaf28e6d1768d0b00fd8"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.1015625,
      "candidate": 0.203125,
      "candidate_minus_baseline": {
        "mean": 0.1015625,
        "ci95": [
          0.03125,
          0.1796875
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 6.111161314416677,
      "candidate": 2.90487808350008,
      "candidate_minus_baseline": {
        "mean": -3.206283230916597,
        "ci95": [
          -4.475019835753483,
          -2.0623101446719376
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.890625,
      "candidate_minus_baseline": {
        "mean": -0.09375,
        "ci95": [
          -0.15625,
          -0.03125
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.39837219619411485,
      "candidate": 0.3907572190268925,
      "candidate_minus_baseline": {
        "mean": -0.007614977167222363,
        "ci95": [
          -0.043603586489215945,
          0.022149107449430137
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.21875,
      "candidate_minus_baseline": {
        "mean": 0.21875,
        "ci95": [
          0.078125,
          0.390625
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 3.2622947208583355,
      "candidate": 1.6888577714562416,
      "candidate_minus_baseline": {
        "mean": -1.5734369494020939,
        "ci95": [
          -1.9625248048221693,
          -1.1782770361518489
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.96875,
      "candidate_minus_baseline": {
        "mean": -0.015625,
        "ci95": [
          -0.0625,
          0.03125
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.2993857629656352,
      "candidate": 0.3259380492138092,
      "candidate_minus_baseline": {
        "mean": 0.026552286248173965,
        "ci95": [
          0.009730840580937256,
          0.04414854570623549
        ],
        "families": 16
      }
    }
  ]
}
```
