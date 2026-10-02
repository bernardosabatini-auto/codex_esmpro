# Matched fragment-conditioning arms

Identical training draws, fragment choices, flow noise/time/dropout/history and initial outputs.500is diagnostic;2000is the prespecified capacity endpoint. Raw motif/geometry scores do not establish designability.

```json
{
  "status": "complete",
  "step": 500,
  "diagnostic_only": true,
  "matched_updates": 500,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "3ba6d46b7e1350a7b9ffe0e2a7d3f17810cf10afe7d6afe1260f03bae03a6376",
    "b6612f1b20cb595619ed8350e56be131a56b107437bcbf8d0a614d70dcc30e0b"
  ],
  "comparisons": [
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "coarse_valid",
      "adapter_only": 0.9921875,
      "full": 0.9765625,
      "full_minus_adapter": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.015625
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "coarse_valid",
      "adapter_only": 0.984375,
      "full": 0.9765625,
      "full_minus_adapter": {
        "mean": -0.0078125,
        "ci95": [
          -0.0390625,
          0.0234375
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "motif_drms",
      "adapter_only": 12.485967813059688,
      "full": 12.267519477754831,
      "full_minus_adapter": {
        "mean": -0.2184483353048563,
        "ci95": [
          -0.4612338456325233,
          0.01622689743526276
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "motif_drms",
      "adapter_only": 13.41431232728064,
      "full": 13.090906370431185,
      "full_minus_adapter": {
        "mean": -0.32340595684945583,
        "ci95": [
          -0.6734932779800147,
          -0.019138849712908426
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "conditioned",
      "metric": "ca_lddt",
      "adapter_only": 0.2705918244334552,
      "full": 0.2759247264748459,
      "full_minus_adapter": {
        "mean": 0.005332902041390737,
        "ci95": [
          -0.0013050886355293967,
          0.011111339367530143
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
      "mode": "null",
      "metric": "ca_lddt",
      "adapter_only": 0.26091556014356776,
      "full": 0.26948366321216666,
      "full_minus_adapter": {
        "mean": 0.008568103068598908,
        "ci95": [
          0.0030251693147576066,
          0.01447519217486472
        ],
        "families": 32
      }
    },
    {
      "cohort": "train",
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
        "families": 32
      }
    },
    {
      "cohort": "train",
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
        "families": 32
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "coarse_valid",
      "adapter_only": 1.0,
      "full": 0.953125,
      "full_minus_adapter": {
        "mean": -0.046875,
        "ci95": [
          -0.09375,
          0.0
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "coarse_valid",
      "adapter_only": 1.0,
      "full": 0.984375,
      "full_minus_adapter": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.0
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "motif_drms",
      "adapter_only": 6.972003236413002,
      "full": 6.690505892038345,
      "full_minus_adapter": {
        "mean": -0.2814973443746567,
        "ci95": [
          -0.5438814898952842,
          -0.052563609369099186
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "motif_drms",
      "adapter_only": 7.328055743128061,
      "full": 7.112388364970684,
      "full_minus_adapter": {
        "mean": -0.21566737815737724,
        "ci95": [
          -0.42840949837118386,
          -0.016198865510523578
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "conditioned",
      "metric": "ca_lddt",
      "adapter_only": 0.2481852078136068,
      "full": 0.24914399226254802,
      "full_minus_adapter": {
        "mean": 0.0009587844489412009,
        "ci95": [
          -0.004363908142314987,
          0.006096226006202675
        ],
        "families": 16
      }
    },
    {
      "cohort": "development",
      "mode": "null",
      "metric": "ca_lddt",
      "adapter_only": 0.24397619939943438,
      "full": 0.24784223941834166,
      "full_minus_adapter": {
        "mean": 0.0038660400189072953,
        "ci95": [
          -0.00012873741699007607,
          0.008128755798007736
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
