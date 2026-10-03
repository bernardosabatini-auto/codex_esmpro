# Preference collection baseline diversity

```json
{
  "status": "complete",
  "manifest_sha256": "717405771f4f26410ea3c0f72776a7fa89933a96fbe60766b1da0e267e813db5",
  "predictions_sha256": "dc0992d7fc118be2090127c89ed6921d9e52dfd5871a57a5ee8815070f25d29c",
  "scorer_sha256": "f7875d048de1ba5df34aa0f0cdae0c0f111f89545dca00ca19d564b1fabab144",
  "summary": [
    {
      "bucket": 128,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.22059333333333334,
      "mean_pair_scaffold_tm": 0.1873466666666667
    },
    {
      "bucket": 256,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.18952645833333334,
      "mean_pair_scaffold_tm": 0.17510937499999998
    },
    {
      "bucket": 384,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.16561479166666668,
      "mean_pair_scaffold_tm": 0.15816249999999998
    },
    {
      "bucket": 512,
      "proteins": 8,
      "pairs": 48,
      "mean_pair_global_tm": 0.15763166666666664,
      "mean_pair_scaffold_tm": 0.15399354166666668
    }
  ],
  "scope": "Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates."
}
```
