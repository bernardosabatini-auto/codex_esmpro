# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control_balanced",
  "manifest_sha256": "b7bd0cc92f8ff458e6e7ba3cf084c2587c875f7364ec4c00b22679cf122ec13a",
  "predictions_sha256": "8c0b74afe81f854f9f33bb3f3773a2876d7917d83bb5aa07afc7794ab13a217e",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 252,
      "raw_matches": 28,
      "mean_motif_ca_rmsd": 3.855085357601989
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 16,
      "mean_motif_ca_rmsd": 3.1528237022147287
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 12,
      "mean_motif_ca_rmsd": 4.557347012989249
    }
  ],
  "controls": 132,
  "elapsed_seconds": 232.47577969776466,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
