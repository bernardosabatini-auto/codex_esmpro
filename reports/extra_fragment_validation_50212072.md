# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "contrastive",
  "manifest_sha256": "5cc18c8fdfd6cda29d1834210389e09cd3ae6beec57ef89b265c151d3f2b4198",
  "predictions_sha256": "fd52b1c48dc199e83f01b98359de5414be8c106d6571a0265b2d3f20c8b3ca3b",
  "summaries": [
    {
      "cohort": "all",
      "samples": 128,
      "families": 32,
      "valid": 128,
      "raw_matches": 31,
      "mean_motif_ca_rmsd": 2.237686677891993
    },
    {
      "cohort": "short",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 23,
      "mean_motif_ca_rmsd": 1.8531337667177417
    },
    {
      "cohort": "long",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 8,
      "mean_motif_ca_rmsd": 2.622239589066244
    }
  ],
  "controls": 68,
  "elapsed_seconds": 141.28120919596404,
  "scope": "Repeated32-protein training-only diagnostic, disjoint from all16native-anchor sources. Not independent generalization. Raw retention does not establish designability."
}
```
