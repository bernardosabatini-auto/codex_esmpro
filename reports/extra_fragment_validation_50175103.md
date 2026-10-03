# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "motif",
  "manifest_sha256": "dfd5b2b41d3ca5f4fc63c314ba1a08a7f1272cb0a8dfc644f6ca63c7cb2a6263",
  "predictions_sha256": "bd2005a9c49dd375ebd472ae6a43cf345ff3a3b44817627414ca98479dcf2cab",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 251,
      "raw_matches": 17,
      "mean_motif_ca_rmsd": 2.7054909182247147
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 126,
      "raw_matches": 12,
      "mean_motif_ca_rmsd": 2.655918741862621
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 5,
      "mean_motif_ca_rmsd": 2.7550630945868084
    }
  ],
  "controls": 132,
  "elapsed_seconds": 248.49676309805363,
  "scope": "Repeated64-family development comparison; equal new parameters, inputs and draws. Only routing differs. No evaluation labels train either model.6000parent and native budgets reused unchanged. Raw retention does not establish designability."
}
```
