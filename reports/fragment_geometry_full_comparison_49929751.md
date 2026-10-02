# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision or shared-trunk learning; every output retained.500diagnostic,2000primary. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "direct_distance_input",
  "matched_updates": 2000,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "755d309ff80bf2eee45e57419bca8c63cc9033ac60a5d0217a7ab8009fee086d",
    "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036"
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
      "baseline": 12.267519477754831,
      "candidate": 10.978376058861613,
      "candidate_minus_baseline": {
        "mean": -1.289143418893218,
        "ci95": [
          -1.5693466807249934,
          -1.017562212375924
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.9765625,
      "candidate": 0.984375,
      "candidate_minus_baseline": {
        "mean": 0.0078125,
        "ci95": [
          -0.0234375,
          0.0390625
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.2759247264748459,
      "candidate": 0.29355316124863534,
      "candidate_minus_baseline": {
        "mean": 0.017628434773789416,
        "ci95": [
          0.010440271579792763,
          0.0258840672287279
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
      "baseline": 6.690505892038345,
      "candidate": 5.533910622820258,
      "candidate_minus_baseline": {
        "mean": -1.1565952692180872,
        "ci95": [
          -1.4793981906957925,
          -0.8377950480673463
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 0.953125,
      "candidate": 1.0,
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
      "metric": "ca_lddt",
      "baseline": 0.24914399226254802,
      "candidate": 0.25966569180543525,
      "candidate_minus_baseline": {
        "mean": 0.010521699542887215,
        "ci95": [
          0.0048297088114128426,
          0.016545869159703908
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.046875,
      "candidate": 0.078125,
      "candidate_minus_baseline": {
        "mean": 0.03125,
        "ci95": [
          0.0078125,
          0.0625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 10.51468673418276,
      "candidate": 6.513468626886606,
      "candidate_minus_baseline": {
        "mean": -4.001218107296154,
        "ci95": [
          -4.9460674128786195,
          -3.0239380214246925
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.9921875,
      "candidate": 0.9921875,
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
      "step": 2000,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.31898082295209274,
      "candidate": 0.37926077491471044,
      "candidate_minus_baseline": {
        "mean": 0.06027995196261769,
        "ci95": [
          0.04305795405506364,
          0.07761508302099274
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.015625,
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
      "metric": "motif_drms",
      "baseline": 5.722377631813288,
      "candidate": 2.8548352206125855,
      "candidate_minus_baseline": {
        "mean": -2.867542411200702,
        "ci95": [
          -3.625804537977092,
          -2.1582819434348495
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
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
      "step": 2000,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.2557026482649809,
      "candidate": 0.299698670813013,
      "candidate_minus_baseline": {
        "mean": 0.04399602254803215,
        "ci95": [
          0.031928208150525494,
          0.056689919771068936
        ],
        "families": 16
      }
    }
  ]
}
```
