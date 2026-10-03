# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "broad_weight3",
  "manifest_sha256": "29365c235bc620b57282239c19c32d61e58f5f5b91a83324dfd4a7972bb4a100",
  "predictions_sha256": "411f64d71c6c3b6e2cfaae623e267913e98128dbc19ede2658e4e9d71c62c3b9",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 249,
      "raw_matches": 50,
      "mean_motif_ca_rmsd": 2.0919623680181747
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 122,
      "raw_matches": 31,
      "mean_motif_ca_rmsd": 1.8483548530822296
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 19,
      "mean_motif_ca_rmsd": 2.33556988295412
    }
  ],
  "controls": 132,
  "elapsed_seconds": 232.45908442465588,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
