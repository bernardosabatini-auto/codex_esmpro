# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control_frozen",
  "manifest_sha256": "d5592a5e85be373fc98690cf889aeab6f69d734f1d3710939cb205c39e7c7499",
  "predictions_sha256": "9d374aa2a1bd77a016a1086c1948e2b28e06817d82bc6d803409e7b79d562cf1",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 251,
      "raw_matches": 18,
      "mean_motif_ca_rmsd": 2.652221811976696
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 125,
      "raw_matches": 11,
      "mean_motif_ca_rmsd": 2.585132191717209
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 126,
      "raw_matches": 7,
      "mean_motif_ca_rmsd": 2.719311432236184
    }
  ],
  "controls": 132,
  "elapsed_seconds": 234.50747207785025,
  "scope": "Repeated64-family development panel, not a locked test. No evaluation labels enter training. Candidate-versus-full and candidate-versus6000-parent comparisons are prespecified separately; native attempts are reused without pooling. Raw retention does not establish designability."
}
```
