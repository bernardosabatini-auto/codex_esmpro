# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control512",
  "manifest_sha256": "4bf75d8ce0c013f0a538d02a5f49a8ae9b95cde639f27bb5216eb13883370f3b",
  "predictions_sha256": "a34cd6979c5675f8334bc81ec595d2d93925237eb3badaa1460a3d4195d40362",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 252,
      "raw_matches": 23,
      "mean_motif_ca_rmsd": 2.6607024818069727
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 13,
      "mean_motif_ca_rmsd": 2.637713488982719
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 10,
      "mean_motif_ca_rmsd": 2.6836914746312264
    }
  ],
  "controls": 132,
  "elapsed_seconds": 253.52989385509863,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
