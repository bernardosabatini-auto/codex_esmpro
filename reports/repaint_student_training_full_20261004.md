# Matched isolated-input endpoint training

```json
{
  "status": "complete",
  "qualified": true,
  "profile_only": false,
  "matched_updates": 400,
  "protocol_sha256": "13afcc9bf98c32900f0ceabc2ddc5eb7bec174d7297bd49ff82dd690b5dd5769",
  "labels_manifest_sha256": "30c92d616143b92c6c565e838d2b42b6b65e3932cfb2889bd396910fb37910d3",
  "training_labels": 13,
  "training_families": 9,
  "initial_predictions_per_arm": 32,
  "recommended_full_minutes": 10,
  "profile_prefix_exact": [
    "native_matched",
    "repaint_positive"
  ],
  "summary": [
    {
      "arm": "native_matched",
      "training_seconds": 68.1700922162272,
      "elapsed_seconds": 143.99188891984522,
      "peak_reserved_GiB": 8.63671875
    },
    {
      "arm": "repaint_positive",
      "training_seconds": 68.04304365068674,
      "elapsed_seconds": 131.08540724916384,
      "peak_reserved_GiB": 8.63671875
    }
  ],
  "scope": "Numerical and resource qualification only. Both arms use identical isolated inputs and random draws; supervised endpoint latents differ. No designability or generalization claim."
}
```
