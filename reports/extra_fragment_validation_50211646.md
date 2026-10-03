# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "positive",
  "manifest_sha256": "af2520242c758d09777a8918969d1617988059503b0f6cb2df6657c9a8104b03",
  "predictions_sha256": "ea006d318ebb8f13bb49161585988f20e50ff2524d4f1bd9ec24acaa40c7789a",
  "summaries": [
    {
      "cohort": "all",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 25,
      "mean_motif_ca_rmsd": 2.3142025826966854
    },
    {
      "cohort": "short",
      "samples": 64,
      "families": 16,
      "valid": 63,
      "raw_matches": 19,
      "mean_motif_ca_rmsd": 1.9252991219703708
    },
    {
      "cohort": "long",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "raw_matches": 6,
      "mean_motif_ca_rmsd": 2.7031060434230003
    }
  ],
  "controls": 68,
  "elapsed_seconds": 145.4850636990741,
  "scope": "Repeated32-protein training-only diagnostic, disjoint from all16native-anchor sources. Not independent generalization. Raw retention does not establish designability."
}
```
