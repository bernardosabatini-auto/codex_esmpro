# Preference collection baseline diversity

```json
{
  "status": "complete",
  "manifest_sha256": "5cc18c8fdfd6cda29d1834210389e09cd3ae6beec57ef89b265c151d3f2b4198",
  "predictions_sha256": "fd52b1c48dc199e83f01b98359de5414be8c106d6571a0265b2d3f20c8b3ca3b",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "summary": [
    {
      "bucket": 128,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.22313562499999998,
      "mean_pair_scaffold_tm": 0.18603791666666666
    },
    {
      "bucket": 256,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.19263937499999997,
      "mean_pair_scaffold_tm": 0.17167624999999997
    },
    {
      "bucket": 384,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.16582520833333333,
      "mean_pair_scaffold_tm": 0.15655624999999998
    },
    {
      "bucket": 512,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.15745833333333334,
      "mean_pair_scaffold_tm": 0.15339270833333332
    }
  ],
  "scope": "Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates."
}
```
