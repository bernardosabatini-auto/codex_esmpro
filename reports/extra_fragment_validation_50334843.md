# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "native_matched",
  "manifest_sha256": "f307fd5b5c5fa7fbcf9b79b3bee65a7aa807026f7abda36bd9e9769e95ad7a8c",
  "predictions_sha256": "304a8eae8288cc0475b19dbe9d287b0cbc80be50596fe5b475b3f5cbed3e9f25",
  "summaries": [
    {
      "cohort": "all",
      "samples": 128,
      "families": 32,
      "valid": 128,
      "raw_matches": 20,
      "mean_motif_ca_rmsd": 2.4858784388804245
    },
    {
      "cohort": "short",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 12,
      "mean_motif_ca_rmsd": 2.2431839392044655
    },
    {
      "cohort": "long",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 8,
      "mean_motif_ca_rmsd": 2.7285729385563826
    }
  ],
  "controls": 68,
  "elapsed_seconds": 146.5059003410861,
  "scope": "Repeated32-training-protein diagnostic. Nine label families and23 other training families are reported separately. No held-out or generalization claim. Raw retention does not establish designability.",
  "label_cohorts": [
    {
      "cohort": "label_families",
      "families": 9,
      "samples": 36,
      "valid": 36,
      "raw": 12
    },
    {
      "cohort": "other_training_families",
      "families": 23,
      "samples": 92,
      "valid": 92,
      "raw": 8
    }
  ],
  "refold_eligibility": {
    "qualified": true,
    "raw": 20,
    "valid": 128
  }
}
```
