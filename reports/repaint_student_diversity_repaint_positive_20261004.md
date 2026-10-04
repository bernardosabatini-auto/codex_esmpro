# Preference collection baseline diversity

```json
{
  "status": "complete",
  "manifest_sha256": "1ce0e88937b28dd75b7642dec5751f3a27a3dfe3b15001346b8bfdab83cabe66",
  "predictions_sha256": "e7486d324a257644fe918cd60b2d841be821e405d65a0217f65b30b26046296d",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "summary": [
    {
      "bucket": 128,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.22702,
      "mean_pair_scaffold_tm": 0.2017314583333333
    },
    {
      "bucket": 256,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.18716541666666664,
      "mean_pair_scaffold_tm": 0.17222520833333332
    },
    {
      "bucket": 384,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.163829375,
      "mean_pair_scaffold_tm": 0.155930625
    },
    {
      "bucket": 512,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.15714208333333332,
      "mean_pair_scaffold_tm": 0.15313104166666666
    }
  ],
  "scope": "Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates."
}
```
