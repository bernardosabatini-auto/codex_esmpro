# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control512",
  "manifest_sha256": "988e7b6a65d8be9541c529c5016960e0cbca3b4f04c9db1e2314af7a81b56901",
  "predictions_sha256": "5c1f37b899d7df09cedbf0027fb1dcc95c4b2cd4e6a11d3e2975f91c86bf29b1",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 252,
      "raw_matches": 24,
      "mean_motif_ca_rmsd": 4.017803101789362
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 14,
      "mean_motif_ca_rmsd": 3.164055744262595
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 10,
      "mean_motif_ca_rmsd": 4.871550459316127
    }
  ],
  "controls": 132,
  "elapsed_seconds": 234.5339652299881,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
