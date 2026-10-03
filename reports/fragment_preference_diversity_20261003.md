# Preference collection baseline diversity

```json
{
  "status": "complete",
  "manifest_sha256": "4ca03c06e16f45dda08fbb8a56aaa5f5a0a1f7566a32d77002ec1053573af3cd",
  "predictions_sha256": "0dc432d41c9ca746646dfa0dae1f063330445c21523a7df280424c1a54ea11b1",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "summary": [
    {
      "bucket": 128,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.21649104166666666,
      "mean_pair_scaffold_tm": 0.18968958333333333
    },
    {
      "bucket": 256,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.188735625,
      "mean_pair_scaffold_tm": 0.173420625
    },
    {
      "bucket": 384,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.16795645833333336,
      "mean_pair_scaffold_tm": 0.15832833333333332
    },
    {
      "bucket": 512,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.15723895833333335,
      "mean_pair_scaffold_tm": 0.15314583333333334
    }
  ],
  "scope": "Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates."
}
```
