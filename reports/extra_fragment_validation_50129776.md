# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control_weight3",
  "manifest_sha256": "af851665f71b87b117e3bd6c14b6ac95d9bf337260ca5bba528d20b0b3c9979e",
  "predictions_sha256": "41adbbc4af8f16668e079628334bd3c8247c4ca9edfd19b00d85399f0ffb5d6c",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 250,
      "raw_matches": 22,
      "mean_motif_ca_rmsd": 2.5053170100515025
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 126,
      "raw_matches": 14,
      "mean_motif_ca_rmsd": 2.4440436503573664
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 8,
      "mean_motif_ca_rmsd": 2.5665903697456383
    }
  ],
  "controls": 132,
  "elapsed_seconds": 236.38744823541492,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
