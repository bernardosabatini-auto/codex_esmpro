# Isolated-fragment context-code flow

Both fixed 2,000-update arms passed exact 40-update profile replay. The validation
loss difference was −0.00817 (95% family bootstrap interval −0.02727 to +0.01021;
16 families, three placements each, 10,000 resamples, seed 2026100902). This does
not establish an improvement. These are families excluded from this adapter's
training, drawn from the old training corpus, not novel-protein benchmarks.

One RTX allocation lasted 42 seconds (0.0117 GPU-hours), including both models.
Peak reserved memory was 0.205 GiB. Assigned-UUID counters gave 7.98% weighted
utilization over 25 captured seconds, excluding startup. This small 805,256-parameter
pilot used little GPU capacity but completed quickly; its percentage is not the
account-wide 24-hour metric. Sampling context codes was included in worker time;
the subsequent scaffold assay is not an end-to-end latency benchmark.

```json
{
  "status": "complete",
  "qualified": true,
  "profile_only": false,
  "updates": 2000,
  "data_manifest_sha256": "6b68e7b861a98a4c6865b7df2f681a2f1a173205f2954597f77ac2f395504604",
  "manifest_sha256": "1030c76374a2bb72bf87d30bf9f6a18f4c938c6aaa7eef5bf7296cc6f183afbe",
  "counts": {
    "train": 464,
    "validation": 16,
    "evaluation": 32
  },
  "recommended_full_minutes": 5,
  "elapsed_seconds": 31.9737731940113,
  "interpretation": "Technical qualification only; loss and sampled latent diversity do not establish structural designability.",
  "arms": {
    "isolated": {
      "training_seconds": 12.211918252054602,
      "peak_reserved_GiB": 0.203125,
      "parameters": 805256,
      "sensitivity": 1.9407145977020264,
      "checkpoint_sha256": "62f5ea93ba0005cd8e47e05ef30c7cc0c083596a103aa18d84c7d4ca50e356d7",
      "codes_sha256": "71492820207c04e7edaf0a570f882be4c4085301a0f8be2a53ce367899e2967c",
      "initial_loss": 2.0076755434274673,
      "final_validation_loss": 0.4941886079808076,
      "final_training_loss": 0.5480393081903457,
      "mean_per_target_code_std": 0.5789496898651123
    },
    "ablated": {
      "training_seconds": 11.82893970888108,
      "peak_reserved_GiB": 0.205078125,
      "parameters": 805256,
      "sensitivity": 0.0,
      "checkpoint_sha256": "6c6af78900bd96b0e265d77d06afb766723200ee5b14b5c0a641817a848f942f",
      "codes_sha256": "00920d9b1da9a50d4f7fc0705403842d1da3a81041a95e8788209d86935291c2",
      "initial_loss": 2.0076755434274673,
      "final_validation_loss": 0.5023537824551264,
      "final_training_loss": 0.5579949647188187,
      "mean_per_target_code_std": 0.5898119211196899
    }
  }
}
```
