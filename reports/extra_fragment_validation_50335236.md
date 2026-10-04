# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "repaint_positive",
  "manifest_sha256": "1ce0e88937b28dd75b7642dec5751f3a27a3dfe3b15001346b8bfdab83cabe66",
  "predictions_sha256": "e7486d324a257644fe918cd60b2d841be821e405d65a0217f65b30b26046296d",
  "summaries": [
    {
      "cohort": "all",
      "samples": 128,
      "families": 32,
      "valid": 128,
      "raw_matches": 22,
      "mean_motif_ca_rmsd": 2.4301547487223694
    },
    {
      "cohort": "short",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 17,
      "mean_motif_ca_rmsd": 2.0798060669372465
    },
    {
      "cohort": "long",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 5,
      "mean_motif_ca_rmsd": 2.7805034305074923
    }
  ],
  "controls": 68,
  "elapsed_seconds": 146.4492118228227,
  "scope": "Repeated32-training-protein diagnostic. Nine label families and23 other training families are reported separately. No held-out or generalization claim. Raw retention does not establish designability.",
  "label_cohorts": [
    {
      "cohort": "label_families",
      "families": 9,
      "samples": 36,
      "valid": 36,
      "raw": 15
    },
    {
      "cohort": "other_training_families",
      "families": 23,
      "samples": 92,
      "valid": 92,
      "raw": 7
    }
  ],
  "refold_eligibility": {
    "qualified": true,
    "raw": 22,
    "valid": 128
  }
}
```
