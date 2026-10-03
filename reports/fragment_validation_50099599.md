# Fresh-noise fragment validation

```json
{
  "status": "complete",
  "manifest_sha256": "990c5ea0ef70786ea0d4cce1454a44808a0923040a38aedc76ab625857b0fc75",
  "predictions_sha256": "563b3f6ab10e995d5ff71fd138fd633b8c63e222c979b27723e432e6f8454022",
  "unique_generated_samples": 152,
  "summaries": [
    {
      "arm": "reference6000",
      "view": "whole_panel",
      "samples": 64,
      "families": 16,
      "valid": 63,
      "strict_raw": 4,
      "families_with_strict_raw": 4,
      "mean_motif_ca_rmsd": 2.1731840782870115
    },
    {
      "arm": "reference6000",
      "view": "focus",
      "samples": 16,
      "families": 1,
      "valid": 16,
      "strict_raw": 3,
      "families_with_strict_raw": 1,
      "mean_motif_ca_rmsd": 1.3653735989965177
    },
    {
      "arm": "augmented8000",
      "view": "whole_panel",
      "samples": 64,
      "families": 16,
      "valid": 63,
      "strict_raw": 8,
      "families_with_strict_raw": 5,
      "mean_motif_ca_rmsd": 1.9468371221611211
    },
    {
      "arm": "augmented8000",
      "view": "focus",
      "samples": 16,
      "families": 1,
      "valid": 16,
      "strict_raw": 6,
      "families_with_strict_raw": 1,
      "mean_motif_ca_rmsd": 1.0857866098464073
    }
  ],
  "elapsed_seconds": 132.44953383179381,
  "interpretation": "Reused development families and one post-selected case, with prospective fresh noise. This tests stochastic repeatability and conditional diversity, not independent-protein validation. No development refolds become training labels; locked tests remain unscored. Keep the failed fixed-panel and other recipe results intact. This compares deployment candidates at different training exposures, not a target-only attribution; the matched 8000-update target-only comparison remains separate. Preserve original seed2026100270 validation. No significance or broad generalization claim from a handful of successes. Views overlap by four samples perarm; raw matches require refolding."
}
```
