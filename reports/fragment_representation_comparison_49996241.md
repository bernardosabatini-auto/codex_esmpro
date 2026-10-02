# Fragment conditioning comparison

Same original checkpoint, matched adapter initialization, data draws and training schedule. The declared contrast adds intramotif distance biases, decoded motif supervision, shared-trunk learning or reference-data breadth; target draws intentionally differ for data breadth; every output retained. Comparison endpoint and matched exposure are explicit in the result; a500update pilot does not represent2000update performance. Training capacity is not designability or generalization.

```json
{
  "status": "complete",
  "contrast": "standalone_latent_input_ablation",
  "matched_updates": 2000,
  "comparison_endpoint": 2000,
  "target_draws_matched": true,
  "identical_initial_samples": 384,
  "source_manifest_hashes": [
    "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
    "a933ada64e326e3bf7fd8c35f29dc44245ed0a61c02ccf624d8ea01e03066731"
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
      "candidate": 11.8761096727103,
      "candidate_minus_baseline": {
        "mean": 0.8977336138486862,
        "ci95": [
          0.6330534261185676,
          1.1748821251560002
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "coarse_valid",
      "baseline": 0.984375,
      "candidate": 0.9921875,
      "candidate_minus_baseline": {
        "mean": 0.0078125,
        "ci95": [
          -0.015625,
          0.03125
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "metric": "ca_lddt",
      "baseline": 0.29355316124863534,
      "candidate": 0.2856636578674168,
      "candidate_minus_baseline": {
        "mean": -0.007889503381218493,
        "ci95": [
          -0.011409458253900039,
          -0.004300163284128592
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
      "candidate": 5.951549364253879,
      "candidate_minus_baseline": {
        "mean": 0.41763874143362045,
        "ci95": [
          0.10309345964342356,
          0.7639594137668609
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
      "baseline": 0.25966569180543525,
      "candidate": 0.2567311573607555,
      "candidate_minus_baseline": {
        "mean": -0.002934534444679714,
        "ci95": [
          -0.00917652310302,
          0.0027046120538054275
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "metric": "joint",
      "baseline": 0.078125,
      "candidate": 0.078125,
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
      "baseline": 6.513468626886606,
      "candidate": 7.880744068650529,
      "candidate_minus_baseline": {
        "mean": 1.3672754417639226,
        "ci95": [
          0.8847429199027829,
          1.8623009354923852
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
      "candidate": 0.3720122102937666,
      "candidate_minus_baseline": {
        "mean": -0.0072485646209438466,
        "ci95": [
          -0.014582733798119746,
          7.717157236599113e-05
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
          -0.046875,
          0.046875
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "metric": "motif_drms",
      "baseline": 2.8548352206125855,
      "candidate": 3.564139454625547,
      "candidate_minus_baseline": {
        "mean": 0.7093042340129614,
        "ci95": [
          0.3482022080337629,
          1.1427842606324703
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
      "candidate": 0.29582035258081596,
      "candidate_minus_baseline": {
        "mean": -0.0038783182321970346,
        "ci95": [
          -0.011763756675513434,
          0.0041977083256907605
        ],
        "families": 16
      }
    }
  ]
}
```
