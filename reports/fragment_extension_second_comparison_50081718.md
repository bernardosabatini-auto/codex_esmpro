# Matched conditioning duration test

```json
{
  "status": "complete",
  "additional_matched_updates": 2000,
  "total_updates_per_arm": 8000,
  "original_pair_matched": true,
  "own_parent_initial_outputs_per_arm": 384,
  "initial_outputs_identical_between_extension_arms": false,
  "comparisons": [
    {
      "cohort": "train",
      "metric": "strict_raw",
      "plain_parent": 0.0859375,
      "weighted_parent": 0.171875,
      "plain_extended": 0.1640625,
      "weighted_extended": 0.25,
      "extended_weighted_minus_plain": {
        "mean": 0.0859375,
        "ci95": [
          0.015625,
          0.1640625
        ],
        "families": 32
      },
      "plain_extension_change": {
        "mean": 0.078125,
        "ci95": [
          0.015625,
          0.1484375
        ],
        "families": 32
      },
      "weighted_extension_change": {
        "mean": 0.078125,
        "ci95": [
          0.03125,
          0.1328125
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "metric": "motif_ca_rmsd",
      "plain_parent": 5.524886306621467,
      "weighted_parent": 4.189874909569411,
      "plain_extended": 5.129507739997864,
      "weighted_extended": 3.6795956780457146,
      "extended_weighted_minus_plain": {
        "mean": -1.4499120619521484,
        "ci95": [
          -2.094942075352093,
          -0.8853912912554186
        ],
        "families": 32
      },
      "plain_extension_change": {
        "mean": -0.3953785666236037,
        "ci95": [
          -0.6948074600661631,
          -0.10529004063911776
        ],
        "families": 32
      },
      "weighted_extension_change": {
        "mean": -0.5102792315236963,
        "ci95": [
          -0.870753345862325,
          -0.1852019365820988
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "metric": "coarse_valid",
      "plain_parent": 0.9921875,
      "weighted_parent": 0.984375,
      "plain_extended": 0.96875,
      "weighted_extended": 0.9765625,
      "extended_weighted_minus_plain": {
        "mean": 0.0078125,
        "ci95": [
          -0.0234375,
          0.0390625
        ],
        "families": 32
      },
      "plain_extension_change": {
        "mean": -0.0234375,
        "ci95": [
          -0.0546875,
          0.0078125
        ],
        "families": 32
      },
      "weighted_extension_change": {
        "mean": -0.0078125,
        "ci95": [
          -0.0234375,
          0.0
        ],
        "families": 32
      }
    },
    {
      "cohort": "development",
      "metric": "strict_raw",
      "plain_parent": 0.015625,
      "weighted_parent": 0.046875,
      "plain_extended": 0.0,
      "weighted_extended": 0.0625,
      "extended_weighted_minus_plain": {
        "mean": 0.0625,
        "ci95": [
          0.0,
          0.140625
        ],
        "families": 16
      },
      "plain_extension_change": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      },
      "weighted_extension_change": {
        "mean": 0.015625,
        "ci95": [
          -0.03125,
          0.0625
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "metric": "motif_ca_rmsd",
      "plain_parent": 3.0043033799930874,
      "weighted_parent": 2.451356986433091,
      "plain_extended": 2.8669598212250227,
      "weighted_extended": 2.271791828305341,
      "extended_weighted_minus_plain": {
        "mean": -0.5951679929196818,
        "ci95": [
          -0.9984268565087452,
          -0.27209840526883666
        ],
        "families": 16
      },
      "plain_extension_change": {
        "mean": -0.1373435587680649,
        "ci95": [
          -0.6104300838387101,
          0.274033962003968
        ],
        "families": 16
      },
      "weighted_extension_change": {
        "mean": -0.1795651581277498,
        "ci95": [
          -0.3929680280998087,
          0.052179809850604
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "metric": "coarse_valid",
      "plain_parent": 1.0,
      "weighted_parent": 0.96875,
      "plain_extended": 1.0,
      "weighted_extended": 0.984375,
      "extended_weighted_minus_plain": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      },
      "plain_extension_change": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      },
      "weighted_extension_change": {
        "mean": 0.015625,
        "ci95": [
          -0.03125,
          0.0625
        ],
        "families": 16
      }
    }
  ],
  "source_manifest_hashes": [
    "83ef2500730cc7c4a11a8b5a30e0d8457e9100dc4212ff5039db53cfb5c94cfa",
    "99d95e43a8745ddd4f7bf9a4e4549f58905bdc64991a63ae7ede7109f322b09d",
    "1d7f19277f9bb37a387e1989593a7d343d7c3d0e8e6070c6e04da87bcb58f54c",
    "18e7e06531eac2d12020b0ac78703a2cbdddd2ad1f6d9c7b821f9e97c0a0cf16"
  ],
  "strict_report_sha256": "7ea0e2cd5cf2cc6b76d4d0a2ce13a6c2f065bc45c122c6c0ceae7244376520da",
  "interpretation": "Fixed development/capacity panels, distinct trained parents and matched continuation exposure. Strict raw retention is not designability. Each final model receives the unchanged same-refold assay; no locked-test claim."
}
```
