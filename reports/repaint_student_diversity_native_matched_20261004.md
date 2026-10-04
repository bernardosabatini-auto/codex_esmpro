# Preference collection baseline diversity

```json
{
  "status": "complete",
  "manifest_sha256": "f307fd5b5c5fa7fbcf9b79b3bee65a7aa807026f7abda36bd9e9769e95ad7a8c",
  "predictions_sha256": "304a8eae8288cc0475b19dbe9d287b0cbc80be50596fe5b475b3f5cbed3e9f25",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "summary": [
    {
      "bucket": 128,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.21319083333333333,
      "mean_pair_scaffold_tm": 0.182569375
    },
    {
      "bucket": 256,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.19123499999999996,
      "mean_pair_scaffold_tm": 0.17392708333333337
    },
    {
      "bucket": 384,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.16524895833333333,
      "mean_pair_scaffold_tm": 0.15709312499999997
    },
    {
      "bucket": 512,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.1576110416666667,
      "mean_pair_scaffold_tm": 0.15415791666666667
    }
  ],
  "scope": "Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates."
}
```
