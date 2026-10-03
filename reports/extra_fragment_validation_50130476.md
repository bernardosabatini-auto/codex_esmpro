# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "broad_balanced",
  "manifest_sha256": "5c8bb1f026849061ca6a88b76f4d5034ffe1e211073168a1960a06b59bcd7ea4",
  "predictions_sha256": "0a84c1284c20cad1bf3034e5fa0827cc1d34a7e99d4d0263f3469d2391a66e5a",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 249,
      "raw_matches": 43,
      "mean_motif_ca_rmsd": 3.492458119756346
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 23,
      "mean_motif_ca_rmsd": 2.5063768734678553
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 20,
      "mean_motif_ca_rmsd": 4.478539366044837
    }
  ],
  "controls": 132,
  "elapsed_seconds": 233.70687925070524,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
