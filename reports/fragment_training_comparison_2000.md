# Matched fragment-conditioning arms

Identical training draws, fragment choices, flow noise/time/dropout/history and initial outputs.500is diagnostic;2000is the prespecified capacity endpoint. Raw motif/geometry scores do not establish designability.

```json
{
  "status": "complete",
  "step": 2000,
  "diagnostic_only": false,
  "matched_updates": 2000,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "3fbef1865392329c3688f43a8dff2a0312f5289716568f9f8d8ca8a9d8647d61",
    "755d309ff80bf2eee45e57419bca8c63cc9033ac60a5d0217a7ab8009fee086d"
  ],
  "comparisons": [
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "coarse_valid",
      "adapter_only": 0.953125,
      "full": 0.9921875,
      "full_minus_adapter": {
        "mean": 0.0390625,
        "ci95": [
          0.0,
          0.078125
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "coarse_valid",
      "adapter_only": 0.984375,
      "full": 0.9921875,
      "full_minus_adapter": {
        "mean": 0.0078125,
        "ci95": [
          -0.015625,
          0.0390625
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "motif_drms",
      "adapter_only": 11.229776890948415,
      "full": 10.51468673418276,
      "full_minus_adapter": {
        "mean": -0.7150901567656547,
        "ci95": [
          -1.5493139205384068,
          0.14999344147508964
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "motif_drms",
      "adapter_only": 13.41431232728064,
      "full": 12.986195495352149,
      "full_minus_adapter": {
        "mean": -0.4281168319284916,
        "ci95": [
          -1.0559483075514435,
          0.1950104631483551
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "ca_lddt",
      "adapter_only": 0.27826801078196806,
      "full": 0.31898082295209274,
      "full_minus_adapter": {
        "mean": 0.04071281217012472,
        "ci95": [
          0.014947536132819395,
          0.06946772235770146
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "ca_lddt",
      "adapter_only": 0.26091556014356776,
      "full": 0.28511876562157795,
      "full_minus_adapter": {
        "mean": 0.024203205478010206,
        "ci95": [
          0.010515225546998958,
          0.03880413386855577
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "joint",
      "adapter_only": 0.0,
      "full": 0.046875,
      "full_minus_adapter": {
        "mean": 0.046875,
        "ci95": [
          0.0,
          0.109375
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "joint",
      "adapter_only": 0.0,
      "full": 0.0078125,
      "full_minus_adapter": {
        "mean": 0.0078125,
        "ci95": [
          0.0,
          0.0234375
        ],
        "families": 32
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "coarse_valid",
      "adapter_only": 0.984375,
      "full": 0.984375,
      "full_minus_adapter": {
        "mean": 0.0,
        "ci95": [
          -0.046875,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "coarse_valid",
      "adapter_only": 1.0,
      "full": 1.0,
      "full_minus_adapter": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "motif_drms",
      "adapter_only": 6.595976756885648,
      "full": 5.722377631813288,
      "full_minus_adapter": {
        "mean": -0.87359912507236,
        "ci95": [
          -1.4830870079342275,
          -0.2509843399282548
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "motif_drms",
      "adapter_only": 7.328055743128061,
      "full": 7.209531173110008,
      "full_minus_adapter": {
        "mean": -0.11852457001805305,
        "ci95": [
          -0.6618069555610419,
          0.38885265197604846
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "ca_lddt",
      "adapter_only": 0.2557642014089006,
      "full": 0.2557026482649809,
      "full_minus_adapter": {
        "mean": -6.155314391974483e-05,
        "ci95": [
          -0.01043959950050812,
          0.00986591753522257
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "ca_lddt",
      "adapter_only": 0.24397619939943438,
      "full": 0.24995132772423506,
      "full_minus_adapter": {
        "mean": 0.005975128324800665,
        "ci95": [
          -0.004365094581010056,
          0.015536170083922362
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "joint",
      "adapter_only": 0.0,
      "full": 0.0,
      "full_minus_adapter": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "joint",
      "adapter_only": 0.0,
      "full": 0.0,
      "full_minus_adapter": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 16
      }
    }
  ]
}
```
