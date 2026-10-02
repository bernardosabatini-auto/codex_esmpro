# Direct fragment-distance conditioning

Same frozen generator, token-adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases or decoded motif supervision; every output retained.500diagnostic,2000primary. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "decoded_motif_objective",
  "matched_updates": 2000,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "c9a329b769b04d4d242e64bd0e68e1a6d2b74ff95f47f4b15c06358326c73653",
    "4046eaa75d48dd0fce3bbe6626827dd7433c16a2841ff3e337d74d222291634b"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.0,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 11.451117880642414,
      "candidate": 11.132528997957706,
      "candidate_minus_baseline": {
        "mean": -0.31858888268470764,
        "ci95": [
          -0.5325879430398345,
          -0.1262235107365998
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 1.0,
      "candidate": 0.9765625,
      "candidate_minus_baseline": {
        "mean": -0.0234375,
        "ci95": [
          -0.0546875,
          0.0
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.28520666552878593,
      "candidate": 0.29033579369098417,
      "candidate_minus_baseline": {
        "mean": 0.0051291281621982515,
        "ci95": [
          0.0031957572871058183,
          0.007323484230215116
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.0,
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
      "metric": "motif_drms",
      "baseline": 5.988396506756544,
      "candidate": 5.793510299175978,
      "candidate_minus_baseline": {
        "mean": -0.1948862075805664,
        "ci95": [
          -0.36541610267013314,
          -0.04576143343001606
        ],
        "families": 16
      }
    },
    {
      "step": 500,
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
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.2611493176242241,
      "candidate": 0.26394150839464336,
      "candidate_minus_baseline": {
        "mean": 0.002792190770419256,
        "ci95": [
          0.0006341370791163939,
          0.005404990349185097
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.0,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 7.216649770736694,
      "candidate": 7.017704332247376,
      "candidate_minus_baseline": {
        "mean": -0.1989454384893179,
        "ci95": [
          -0.39580322047695515,
          -0.0004062203923240819
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.96875,
      "candidate": 0.96875,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          -0.03125,
          0.03125
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.33061122308685165,
      "candidate": 0.33545569079762283,
      "candidate_minus_baseline": {
        "mean": 0.004844467710771134,
        "ci95": [
          0.0023975785126293322,
          0.007426000574235776
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.0,
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
      "metric": "motif_drms",
      "baseline": 3.1949331536889076,
      "candidate": 3.003804737702012,
      "candidate_minus_baseline": {
        "mean": -0.19112841598689556,
        "ci95": [
          -0.40527184498496355,
          -0.0002418392803520921
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
      "baseline": 0.29231344724552755,
      "candidate": 0.29369148355574726,
      "candidate_minus_baseline": {
        "mean": 0.0013780363102196998,
        "ci95": [
          -0.0012056157632466076,
          0.0041997256945598025
        ],
        "families": 16
      }
    }
  ],
  "objective_gate_passed": false
}
```
