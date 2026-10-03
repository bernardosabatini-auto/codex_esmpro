# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control_balanced",
  "manifest_sha256": "c87b6226613ed59d158659bea1cfc07f7af772d593b65b2761739becf5286140",
  "predictions_sha256": "73b7026d7ace6a155542624ce3b65765c8ff3e986d34ed335e758719b07451a7",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 250,
      "raw_matches": 17,
      "mean_motif_ca_rmsd": 2.5619663469137937
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 126,
      "raw_matches": 9,
      "mean_motif_ca_rmsd": 2.4665879094705554
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 8,
      "mean_motif_ca_rmsd": 2.657344784357033
    }
  ],
  "controls": 132,
  "elapsed_seconds": 235.49500233028084,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
