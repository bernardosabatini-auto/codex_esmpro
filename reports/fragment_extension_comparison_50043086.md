# Matched conditioning duration test

```json
{
  "status": "complete",
  "additional_matched_updates": 2000,
  "total_updates_per_arm": 6000,
  "original_pair_matched": true,
  "own_parent_initial_outputs_per_arm": 384,
  "initial_outputs_identical_between_extension_arms": false,
  "comparisons": [
    {
      "cohort": "train",
      "metric": "strict_raw",
      "plain_parent": 0.03125,
      "weighted_parent": 0.09375,
      "plain_extended": 0.0859375,
      "weighted_extended": 0.171875,
      "extended_weighted_minus_plain": {
        "mean": 0.0859375,
        "ci95": [
          0.0078125,
          0.171875
        ],
        "families": 32
      },
      "plain_extension_change": {
        "mean": 0.0546875,
        "ci95": [
          -0.00019531249999982236,
          0.1328125
        ],
        "families": 32
      },
      "weighted_extension_change": {
        "mean": 0.078125,
        "ci95": [
          0.0078125,
          0.15625
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "metric": "motif_ca_rmsd",
      "plain_parent": 6.3665347830686105,
      "weighted_parent": 5.368250029755223,
      "plain_extended": 5.524886306621467,
      "weighted_extended": 4.189874909569411,
      "extended_weighted_minus_plain": {
        "mean": -1.3350113970520558,
        "ci95": [
          -1.8564519197203628,
          -0.8834948161934877
        ],
        "families": 32
      },
      "plain_extension_change": {
        "mean": -0.841648476447144,
        "ci95": [
          -1.2676361457376732,
          -0.42819664682889375
        ],
        "families": 32
      },
      "weighted_extension_change": {
        "mean": -1.178375120185812,
        "ci95": [
          -1.6800030149841643,
          -0.7085955228951424
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "metric": "coarse_valid",
      "plain_parent": 0.9921875,
      "weighted_parent": 1.0,
      "plain_extended": 0.9921875,
      "weighted_extended": 0.984375,
      "extended_weighted_minus_plain": {
        "mean": -0.0078125,
        "ci95": [
          -0.03125,
          0.015625
        ],
        "families": 32
      },
      "plain_extension_change": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
          0.0234375
        ],
        "families": 32
      },
      "weighted_extension_change": {
        "mean": -0.015625,
        "ci95": [
          -0.0390625,
          0.0
        ],
        "families": 32
      }
    },
    {
      "cohort": "development",
      "metric": "strict_raw",
      "plain_parent": 0.0,
      "weighted_parent": 0.03125,
      "plain_extended": 0.015625,
      "weighted_extended": 0.046875,
      "extended_weighted_minus_plain": {
        "mean": 0.03125,
        "ci95": [
          -0.03125,
          0.09375
        ],
        "families": 16
      },
      "plain_extension_change": {
        "mean": 0.015625,
        "ci95": [
          0.0,
          0.046875
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
      "plain_parent": 3.3832445861056253,
      "weighted_parent": 2.7031653013876786,
      "plain_extended": 3.0043033799930874,
      "weighted_extended": 2.451356986433091,
      "extended_weighted_minus_plain": {
        "mean": -0.552946393559997,
        "ci95": [
          -0.9822936499662362,
          -0.1904143608145384
        ],
        "families": 16
      },
      "plain_extension_change": {
        "mean": -0.37894120611253795,
        "ci95": [
          -0.7713894252374494,
          -0.0016393632919587831
        ],
        "families": 16
      },
      "weighted_extension_change": {
        "mean": -0.2518083149545879,
        "ci95": [
          -0.5792812807939232,
          0.051929271286476
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "metric": "coarse_valid",
      "plain_parent": 1.0,
      "weighted_parent": 0.984375,
      "plain_extended": 1.0,
      "weighted_extended": 0.96875,
      "extended_weighted_minus_plain": {
        "mean": -0.03125,
        "ci95": [
          -0.078125,
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
        "mean": -0.015625,
        "ci95": [
          -0.0625,
          0.03125
        ],
        "families": 16
      }
    }
  ],
  "source_manifest_hashes": [
    "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
    "6e2a7aa446e6ccbd7bd02d1c02de7f741c8ab9a4c6c222e35d0dc0042a2b6285",
    "83ef2500730cc7c4a11a8b5a30e0d8457e9100dc4212ff5039db53cfb5c94cfa",
    "99d95e43a8745ddd4f7bf9a4e4549f58905bdc64991a63ae7ede7109f322b09d"
  ],
  "strict_report_sha256": "b86d9f2520672d272966e1b16f36fa48f5b0b82988e9348d18a65a8e589cb86b",
  "interpretation": "Fixed development/capacity panels, distinct trained parents and matched continuation exposure. Strict raw retention is not designability. Each final model receives the unchanged same-refold assay; no locked-test claim."
}
```
