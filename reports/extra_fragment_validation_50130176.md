# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control_weight3",
  "manifest_sha256": "0817368285640ad7bbd80f97726bbe5a0c8594a264ac5a2bea46e25ee26f76f0",
  "predictions_sha256": "c5ac12415b3c4ded30fdd7dd21db5ed369c00b3a5bd7dcea853d39aeb7cae2b8",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 254,
      "raw_matches": 30,
      "mean_motif_ca_rmsd": 3.75289827420237
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 17,
      "mean_motif_ca_rmsd": 3.0429879189507663
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 13,
      "mean_motif_ca_rmsd": 4.462808629453976
    }
  ],
  "controls": 132,
  "elapsed_seconds": 232.6588611858897,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
