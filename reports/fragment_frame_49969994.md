# Fragment-anchored target-frame probe

```json
{
  "status": "complete",
  "manifest_sha256": "1e69a706abf9a35f687ea3298e55d30cbcb44bc1adcdc81549600ffffd654a7b",
  "predictions_sha256": "9426fc24eaf3f8745d0ae07f852baedd06ae947fa64c017d4219bb3933078b37",
  "conditions": 24,
  "training_families": 8,
  "latent_before_rmse": 0.8533755466341972,
  "latent_after_rmse": 0.5126090532479187,
  "relative_latent_gap_reduction": 0.39931598078981445,
  "before_minus_after_family_interval": {
    "mean": 0.34076649338627857,
    "ci95": [
      0.29022544164520997,
      0.3887527260618905
    ],
    "families": 8
  },
  "mean_full_target_latent_change_rmse": 0.9048520568758249,
  "valid_reconstruction_under_half_A": {
    "original": 24,
    "anchored": 24
  },
  "target_frame_training_qualified": true,
  "interpretation": "Training-only representation diagnostic. Targets already use whole-protein PCA; anchoring changes that convention. This is not generation, generalization or designability evidence.",
  "elapsed_seconds": 35.532482692971826,
  "peak_reserved_GiB": 1.095703125
}
```
