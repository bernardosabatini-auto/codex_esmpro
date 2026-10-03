# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "null512",
  "manifest_sha256": "f561bd2a885417d7b0f7834c73aa21a5ba349f9ce651a7e4f931655ea459491b",
  "predictions_sha256": "a2dfb9685289b9adcfee5f8a46efb8a81c03b1d817bfbef23fbc4cd44da6fac4",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 251,
      "raw_matches": 1,
      "mean_motif_ca_rmsd": 6.377827529855294
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 1,
      "mean_motif_ca_rmsd": 6.286680316827659
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 0,
      "mean_motif_ca_rmsd": 6.46897474288293
    }
  ],
  "controls": 132,
  "elapsed_seconds": 253.57682754984125,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
