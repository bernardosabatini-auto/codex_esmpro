# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "quality",
  "manifest_sha256": "0ec23eedba5be50eb07c97fcc2bd7a0bb4da98eb42d2c252d2c4b82704f66eb2",
  "predictions_sha256": "0bd7be50ea8b2c87f7fd811a603d63523f591f03c5e4d7a768f37c3f293293f0",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 248,
      "raw_matches": 28,
      "mean_motif_ca_rmsd": 2.6147344052040147
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 19,
      "mean_motif_ca_rmsd": 2.439743401848939
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 9,
      "mean_motif_ca_rmsd": 2.7897254085590895
    }
  ],
  "controls": 132,
  "elapsed_seconds": 231.4974981280975,
  "scope": "Repeated64-family development comparison. Training-condition quality alone differs between new arms; teacher-kernel policy is shared. No evaluation labels train either model. The6000parent and original native attempts are historical references, not new pooled budgets. Raw retention does not establish designability."
}
```
