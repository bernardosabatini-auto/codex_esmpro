# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "direct_backbone_token_input",
  "matched_updates": 2000,
  "comparison_endpoint": 2000,
  "target_draws_matched": true,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
    "95527548e361bcece2653a74ed9e2404bfd9a2c1bc7ef53299af98a0176b7bab"
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
      "baseline": 10.978376058861613,
      "candidate": 10.010486510582268,
      "candidate_minus_baseline": {
        "mean": -0.967889548279345,
        "ci95": [
          -1.6169193425448611,
          -0.5046348094707355
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
          -0.03125,
          0.015625
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.29355316124863534,
      "candidate": 0.2981093557069403,
      "candidate_minus_baseline": {
        "mean": 0.004556194458304923,
        "ci95": [
          0.00018393043319372108,
          0.00981796074683228
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
      "baseline": 5.533910622820258,
      "candidate": 5.296535534784198,
      "candidate_minus_baseline": {
        "mean": -0.23737508803606033,
        "ci95": [
          -0.3899374736007303,
          -0.09986945143900823
        ],
        "families": 16
      }
    },
    {
      "step": 500,
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
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.25966569180543525,
      "candidate": 0.2616649112174879,
      "candidate_minus_baseline": {
        "mean": 0.0019992194120526836,
        "ci95": [
          -0.0015569236099950011,
          0.0062499934367222796
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.078125,
      "candidate": 0.0703125,
      "candidate_minus_baseline": {
        "mean": -0.0078125,
        "ci95": [
          -0.0234375,
          0.0
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 6.513468626886606,
      "candidate": 6.136612959206104,
      "candidate_minus_baseline": {
        "mean": -0.37685566768050194,
        "ci95": [
          -0.6893885149096605,
          -0.11058039047056811
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
      "baseline": 0.37926077491471044,
      "candidate": 0.38548403990858204,
      "candidate_minus_baseline": {
        "mean": 0.006223264993871579,
        "ci95": [
          -0.0008842138868980479,
          0.012542464370061103
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.015625,
      "candidate": 0.015625,
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
      "baseline": 2.8548352206125855,
      "candidate": 2.8677949281409383,
      "candidate_minus_baseline": {
        "mean": 0.012959707528352737,
        "ci95": [
          -0.16974948048591612,
          0.2034773194696754
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 0.96875,
      "candidate": 1.0,
      "candidate_minus_baseline": {
        "mean": 0.03125,
        "ci95": [
          0.0,
          0.078125
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.299698670813013,
      "candidate": 0.2957479707125181,
      "candidate_minus_baseline": {
        "mean": -0.003950700100494886,
        "ci95": [
          -0.009442874457790356,
          0.0007899607278319578
        ],
        "families": 16
      }
    }
  ]
}
```
