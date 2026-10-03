# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "augmented512",
  "manifest_sha256": "20d50f1e03d66155dd76f23f7b09a18559b9502bd74c9183388d70490b15140f",
  "predictions_sha256": "d5566e33f0741a99984eb29ef72d7cdd89760318c0acc8ebe8321e9427f436a9",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 255,
      "raw_matches": 22,
      "mean_motif_ca_rmsd": 3.9282965189187435
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 11,
      "mean_motif_ca_rmsd": 3.054748449631499
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 128,
      "raw_matches": 11,
      "mean_motif_ca_rmsd": 4.801844588205988
    }
  ],
  "controls": 132,
  "elapsed_seconds": 236.50078860484064,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
