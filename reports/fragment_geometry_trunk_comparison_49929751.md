# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision or shared-trunk learning; every output retained.500diagnostic,2000primary. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "trainable_trunk",
  "matched_updates": 2000,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "c9a329b769b04d4d242e64bd0e68e1a6d2b74ff95f47f4b15c06358326c73653",
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
      "baseline": 11.451117880642414,
      "candidate": 10.978376058861613,
      "candidate_minus_baseline": {
        "mean": -0.4727418217808008,
        "ci95": [
          -0.8256871602497995,
          -0.14270449629984808
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 1.0,
      "candidate": 0.984375,
      "candidate_minus_baseline": {
        "mean": -0.015625,
        "ci95": [
          -0.0390625,
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
      "candidate": 0.29355316124863534,
      "candidate_minus_baseline": {
        "mean": 0.008346495719849398,
        "ci95": [
          0.002411339388310707,
          0.0139823204843694
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
      "candidate": 5.533910622820258,
      "candidate_minus_baseline": {
        "mean": -0.454485883936286,
        "ci95": [
          -0.841406996641308,
          -0.10417972868308428
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
      "candidate": 0.25966569180543525,
      "candidate_minus_baseline": {
        "mean": -0.0014836258187888654,
        "ci95": [
          -0.007547998524800795,
          0.00405942757145586
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0,
      "candidate": 0.078125,
      "candidate_minus_baseline": {
        "mean": 0.078125,
        "ci95": [
          0.015625,
          0.15625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 7.216649770736694,
      "candidate": 6.513468626886606,
      "candidate_minus_baseline": {
        "mean": -0.7031811438500881,
        "ci95": [
          -1.2320329822134226,
          -0.12061333038145677
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.96875,
      "candidate": 0.9921875,
      "candidate_minus_baseline": {
        "mean": 0.0234375,
        "ci95": [
          -0.0078125,
          0.0546875
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.33061122308685165,
      "candidate": 0.37926077491471044,
      "candidate_minus_baseline": {
        "mean": 0.04864955182785875,
        "ci95": [
          0.02459204895062661,
          0.07557304464862503
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
      "baseline": 3.1949331536889076,
      "candidate": 2.8548352206125855,
      "candidate_minus_baseline": {
        "mean": -0.3400979330763221,
        "ci95": [
          -0.6168510453542695,
          -0.07721213265322154
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 1.0,
      "candidate": 0.96875,
      "candidate_minus_baseline": {
        "mean": -0.03125,
        "ci95": [
          -0.078125,
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
      "candidate": 0.299698670813013,
      "candidate_minus_baseline": {
        "mean": 0.00738522356748548,
        "ci95": [
          -0.002069850573867234,
          0.016341271680637738
        ],
        "families": 16
      }
    }
  ]
}
```
