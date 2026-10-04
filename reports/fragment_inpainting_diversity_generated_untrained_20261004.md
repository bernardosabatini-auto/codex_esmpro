# Coordinate-inpainting scaffold diversity

```json
{
  "status": "complete",
  "manifest_sha256": "ce4ff9c7b685e76c5000dbe3116c721114551f394fe4d5c37c9bb9769e7f04a0",
  "predictions_sha256": "ae1da9f8ca774ec4e8b7da42e4f552fd182b3af7103ab81e92345e09980904a4",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "prediction_group": "generated_untrained",
  "summary": [
    {
      "bucket": null,
      "subset": "all",
      "pairs": 192,
      "proteins": 32,
      "mean_global_tm": 0.19091499999999997,
      "mean_scaffold_tm": 0.16952062499999998
    },
    {
      "bucket": 128,
      "subset": "all",
      "pairs": 48,
      "proteins": 8,
      "mean_global_tm": 0.24149416666666668,
      "mean_scaffold_tm": 0.19132354166666668
    },
    {
      "bucket": 256,
      "subset": "all",
      "pairs": 48,
      "proteins": 8,
      "mean_global_tm": 0.19602395833333333,
      "mean_scaffold_tm": 0.1748502083333333
    },
    {
      "bucket": 384,
      "subset": "all",
      "pairs": 48,
      "proteins": 8,
      "mean_global_tm": 0.16879520833333336,
      "mean_scaffold_tm": 0.1587075
    },
    {
      "bucket": 512,
      "subset": "all",
      "pairs": 48,
      "proteins": 8,
      "mean_global_tm": 0.15734666666666666,
      "mean_scaffold_tm": 0.15320124999999998
    }
  ],
  "scope": "All192 unfiltered training-panel pairs. No success labels used. The final comparison joins strict same-refold outcomes before judging useful diversity."
}
```
