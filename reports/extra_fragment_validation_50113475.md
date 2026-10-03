# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "augmented128",
  "manifest_sha256": "779fe4a84c0e959f1b30a68e2c9e940c6023740933d5415d031070a8b19006d7",
  "predictions_sha256": "e31a555c4aade643266e092d46c2b275ba2f256bf83a838f53a413d8aa68b2bc",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 253,
      "raw_matches": 19,
      "mean_motif_ca_rmsd": 3.829105663294126
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 6,
      "mean_motif_ca_rmsd": 3.3294667962827535
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 126,
      "raw_matches": 13,
      "mean_motif_ca_rmsd": 4.328744530305499
    }
  ],
  "controls": 132,
  "elapsed_seconds": 255.52393670007586,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
