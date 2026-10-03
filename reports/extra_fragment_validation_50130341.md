# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "broad_weight3",
  "manifest_sha256": "776f16f7227c617c5542cb340b2afd66a12922a8dd30261558102fc9d32cf492",
  "predictions_sha256": "8f54bca840c6a20d1fe242efbef6cc17fde29de348f217eb97c34a5db772d83b",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 248,
      "raw_matches": 46,
      "mean_motif_ca_rmsd": 3.299102929747429
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 27,
      "mean_motif_ca_rmsd": 2.3656461458367506
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 19,
      "mean_motif_ca_rmsd": 4.232559713658107
    }
  ],
  "controls": 132,
  "elapsed_seconds": 235.69625693699345,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
