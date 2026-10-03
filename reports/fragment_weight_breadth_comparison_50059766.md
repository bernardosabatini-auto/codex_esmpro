# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "conditional_latent_motif_weight",
  "matched_updates": 2000,
  "comparison_endpoint": 2000,
  "target_draws_matched": true,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "d5f2beac7d19ba5d16c76509a1b1b039a8db13523910d93da62ed086c3d16b68",
    "970cac4541cf5b317bfea08a86801a89712a3e64e7d37561906c4119f64c4297"
  ],
  "comparisons": [
    {
      "step": 500,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.0703125,
      "candidate": 0.140625,
      "candidate_minus_baseline": {
        "mean": 0.0703125,
        "ci95": [
          0.0078125,
          0.140625
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 5.654690294060856,
      "candidate": 5.2359680163208395,
      "candidate_minus_baseline": {
        "mean": -0.4187222777400166,
        "ci95": [
          -0.6203391231014393,
          -0.2703257803688757
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
      "baseline": 0.360505610008572,
      "candidate": 0.3692309026579509,
      "candidate_minus_baseline": {
        "mean": 0.008725292649378907,
        "ci95": [
          0.0044956281398793535,
          0.012790593219814727
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.046875,
      "candidate": 0.0625,
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
      "step": 500,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 2.271076229400933,
      "candidate": 2.1419564429670572,
      "candidate_minus_baseline": {
        "mean": -0.12911978643387556,
        "ci95": [
          -0.20590169508941472,
          -0.05347570474259556
        ],
        "families": 16
      }
    },
    {
      "step": 500,
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
      "step": 500,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.3130722571925958,
      "candidate": 0.3184893301082996,
      "candidate_minus_baseline": {
        "mean": 0.005417072915703838,
        "ci95": [
          0.0016507091039796213,
          0.009652544165584812
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.1953125,
      "candidate": 0.296875,
      "candidate_minus_baseline": {
        "mean": 0.1015625,
        "ci95": [
          0.046875,
          0.1640625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "motif_drms",
      "baseline": 4.251999533735216,
      "candidate": 3.688294568564743,
      "candidate_minus_baseline": {
        "mean": -0.5637049651704729,
        "ci95": [
          -0.910431377403438,
          -0.28336651144782093
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 1.0,
      "candidate": 1.0,
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
      "metric": "ca_lddt",
      "baseline": 0.3789949035823284,
      "candidate": 0.3876193010936789,
      "candidate_minus_baseline": {
        "mean": 0.008624397511350503,
        "ci95": [
          0.005035864575881022,
          0.013105449669326766
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "joint",
      "baseline": 0.234375,
      "candidate": 0.359375,
      "candidate_minus_baseline": {
        "mean": 0.125,
        "ci95": [
          0.03125,
          0.21875
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 1.7227803831920028,
      "candidate": 1.4564803279936314,
      "candidate_minus_baseline": {
        "mean": -0.2663000551983714,
        "ci95": [
          -0.49636643528938296,
          -0.1232099957065657
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.984375,
      "candidate_minus_baseline": {
        "mean": 0.0,
        "ci95": [
          -0.046875,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "ca_lddt",
      "baseline": 0.3284321717242533,
      "candidate": 0.3296658230883489,
      "candidate_minus_baseline": {
        "mean": 0.0012336513640955997,
        "ci95": [
          -0.00529305794985729,
          0.0072038617947513955
        ],
        "families": 16
      }
    }
  ]
}
```
