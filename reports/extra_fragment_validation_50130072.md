# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "broad_balanced",
  "manifest_sha256": "9b14d4f49aee60a455b0602c07203f2acfaea288c56e9a5a153b82e9c0ed629e",
  "predictions_sha256": "184013a35e04adb5b0d55b16a9d1946ca5c0dd769265fb516721cf5725fc8ff2",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 251,
      "raw_matches": 45,
      "mean_motif_ca_rmsd": 2.108408247582531
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 31,
      "mean_motif_ca_rmsd": 1.8809782881146655
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 14,
      "mean_motif_ca_rmsd": 2.335838207050398
    }
  ],
  "controls": 132,
  "elapsed_seconds": 232.38986839121208,
  "scope": "Additional development replication on previously unused conditioning families from an already-used prediction-development corpus. Sequence exclusions are heuristic; frozen-model pretraining exposure is unknown. All locked tests remain unscored and no new evaluation outputs enter training. Raw retention does not establish designability."
}
```
