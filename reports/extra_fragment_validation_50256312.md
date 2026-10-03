# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "positive_coverage",
  "manifest_sha256": "717405771f4f26410ea3c0f72776a7fa89933a96fbe60766b1da0e267e813db5",
  "predictions_sha256": "dc0992d7fc118be2090127c89ed6921d9e52dfd5871a57a5ee8815070f25d29c",
  "summaries": [
    {
      "cohort": "all",
      "samples": 128,
      "families": 32,
      "valid": 128,
      "raw_matches": 23,
      "mean_motif_ca_rmsd": 2.35808254138088
    },
    {
      "cohort": "short",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 16,
      "mean_motif_ca_rmsd": 2.0349796191333502
    },
    {
      "cohort": "long",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 7,
      "mean_motif_ca_rmsd": 2.6811854636284105
    }
  ],
  "controls": 68,
  "elapsed_seconds": 145.5084683811292,
  "scope": "Repeated32-protein training-only diagnostic disjoint from all16 original anchor sources and all64 new qualification sources. Not independent generalization. Raw retention does not establish designability."
}
```
