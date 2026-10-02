# Direct fragment-distance conditioning

Same frozen generator, token-adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases or decoded motif supervision; every output retained.500diagnostic,2000primary. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "direct_distance_input",
  "matched_updates": 2000,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "3fbef1865392329c3688f43a8dff2a0312f5289716568f9f8d8ca8a9d8647d61",
    "c9a329b769b04d4d242e64bd0e68e1a6d2b74ff95f47f4b15c06358326c73653"
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
      "baseline": 12.485967813059688,
      "candidate": 11.451117880642414,
      "candidate_minus_baseline": {
        "mean": -1.0348499324172735,
        "ci95": [
          -1.3616847575642168,
          -0.7068505024071784
        ],
        "families": 32
      }
    },
    {
      "step": 500,
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
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.2705918244334552,
      "candidate": 0.28520666552878593,
      "candidate_minus_baseline": {
        "mean": 0.014614841095330754,
        "ci95": [
          0.009563853176078819,
          0.020186462904447065
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
      "baseline": 6.972003236413002,
      "candidate": 5.988396506756544,
      "candidate_minus_baseline": {
        "mean": -0.9836067296564579,
        "ci95": [
          -1.3386434164829553,
          -0.6244482501409948
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
      "baseline": 0.2481852078136068,
      "candidate": 0.2611493176242241,
      "candidate_minus_baseline": {
        "mean": 0.012964109810617281,
        "ci95": [
          0.007777725639575522,
          0.018269110355155785
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
      "baseline": 11.229776890948415,
      "candidate": 7.216649770736694,
      "candidate_minus_baseline": {
        "mean": -4.0131271202117205,
        "ci95": [
          -4.866848229756579,
          -3.0652893472928557
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.953125,
      "candidate": 0.96875,
      "candidate_minus_baseline": {
        "mean": 0.015625,
        "ci95": [
          -0.0234375,
          0.0625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.27826801078196806,
      "candidate": 0.33061122308685165,
      "candidate_minus_baseline": {
        "mean": 0.05234321230488366,
        "ci95": [
          0.04090866580013747,
          0.06412384469983089
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
      "baseline": 6.595976756885648,
      "candidate": 3.1949331536889076,
      "candidate_minus_baseline": {
        "mean": -3.40104360319674,
        "ci95": [
          -4.137669527484104,
          -2.6395022479817274
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
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
      "step": 2000,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.2557642014089006,
      "candidate": 0.29231344724552755,
      "candidate_minus_baseline": {
        "mean": 0.03654924583662692,
        "ci95": [
          0.024815552530858438,
          0.047820167039631774
        ],
        "families": 16
      }
    }
  ]
}
```
