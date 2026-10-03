# Bounded decoder correction

```json
{
  "status": "complete",
  "manifest_sha256": "7f821fe6253c070669eec6086041938e8cde500e21799c84c7ad9b61a77bab82",
  "predictions_sha256": "12c4e3a896a05a6c11097a1a83efe66ee41e304008ed829d9e7c4d36040caec1",
  "controls": 24,
  "summaries": {
    "initial": {
      "samples": 16,
      "valid": 15,
      "strict_raw": 2,
      "mean_proper_rmsd": 1.4912859281527222
    },
    "guided": {
      "samples": 16,
      "valid": 15,
      "strict_raw": 13,
      "mean_proper_rmsd": 0.5986044335219556
    }
  },
  "newly_invalid_samples": 0,
  "qualified_improved_samples": 13,
  "refold_gate_passed": true,
  "max_relative_displacement": 0.03895788639783859,
  "proposal_batches": 57,
  "incremental_correction_seconds": 3.4905910841189325,
  "max_reserved_GiB": 3.2578125,
  "scope": "Four reused development families,16paired cached starts. Raw fit and latent-statistic preservation do not establish designability. Incremental correction time excludes cached parent generation; no end-to-end speed claim."
}
```
