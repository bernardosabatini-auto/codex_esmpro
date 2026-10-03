# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control128",
  "manifest_sha256": "b1f3b67cad0c9a9c32758b4b69121293cb796dc0154acee4522a15255fafaab6",
  "predictions_sha256": "09634676a593867c1401cc0dc16de72397631e9d4b7d2842d19cc067f7a01a91",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 249,
      "raw_matches": 23,
      "mean_motif_ca_rmsd": 3.854496760012694
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 9,
      "mean_motif_ca_rmsd": 3.387159916449325
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 14,
      "mean_motif_ca_rmsd": 4.321833603576063
    }
  ],
  "controls": 132,
  "elapsed_seconds": 234.4840232427232,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
