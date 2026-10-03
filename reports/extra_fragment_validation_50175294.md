# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "all",
  "manifest_sha256": "d6aa95dbbd99eb1d42d6cce17c3085353fb3e03018e31fb43572e186af970644",
  "predictions_sha256": "486651238f784dc09b8e42d6f510d9f164f423638f6ab1f5100c8a49848925ab",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 252,
      "raw_matches": 18,
      "mean_motif_ca_rmsd": 2.684728181142378
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 128,
      "raw_matches": 11,
      "mean_motif_ca_rmsd": 2.6326983021566197
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 7,
      "mean_motif_ca_rmsd": 2.7367580601281363
    }
  ],
  "controls": 132,
  "elapsed_seconds": 245.41235950076953,
  "scope": "Repeated64-family development comparison; equal new parameters, inputs and draws. Only routing differs. No evaluation labels train either model.6000parent and native budgets reused unchanged. Raw retention does not establish designability."
}
```
