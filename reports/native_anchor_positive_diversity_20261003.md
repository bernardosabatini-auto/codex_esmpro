# Preference collection baseline diversity

```json
{
  "status": "complete",
  "manifest_sha256": "af2520242c758d09777a8918969d1617988059503b0f6cb2df6657c9a8104b03",
  "predictions_sha256": "ea006d318ebb8f13bb49161585988f20e50ff2524d4f1bd9ec24acaa40c7789a",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "summary": [
    {
      "bucket": 128,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.21488270833333334,
      "mean_pair_scaffold_tm": 0.183995625
    },
    {
      "bucket": 256,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.19098791666666667,
      "mean_pair_scaffold_tm": 0.17094958333333332
    },
    {
      "bucket": 384,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.164170625,
      "mean_pair_scaffold_tm": 0.15704895833333332
    },
    {
      "bucket": 512,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.15734770833333334,
      "mean_pair_scaffold_tm": 0.15349625
    }
  ],
  "scope": "Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates."
}
```
