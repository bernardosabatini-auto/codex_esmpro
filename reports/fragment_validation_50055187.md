# Fresh-noise fragment validation

```json
{
  "status": "complete",
  "manifest_sha256": "cb4dd4248263d477e30c9f524fe302ef29aed735ca6c4aafe77d841b2f99c5e4",
  "predictions_sha256": "d8218b80d055a9e53d5bd7f31b5b88eed0306966df6c0f6de89621a13a2d5bfc",
  "unique_generated_samples": 152,
  "summaries": [
    {
      "arm": "plain",
      "view": "whole_panel",
      "samples": 64,
      "families": 16,
      "valid": 64,
      "strict_raw": 2,
      "families_with_strict_raw": 1,
      "mean_motif_ca_rmsd": 2.7857953853522686
    },
    {
      "arm": "plain",
      "view": "focus",
      "samples": 16,
      "families": 1,
      "valid": 16,
      "strict_raw": 0,
      "families_with_strict_raw": 0,
      "mean_motif_ca_rmsd": 1.7943377866976082
    },
    {
      "arm": "weighted",
      "view": "whole_panel",
      "samples": 64,
      "families": 16,
      "valid": 62,
      "strict_raw": 5,
      "families_with_strict_raw": 3,
      "mean_motif_ca_rmsd": 2.0759360365024975
    },
    {
      "arm": "weighted",
      "view": "focus",
      "samples": 16,
      "families": 1,
      "valid": 16,
      "strict_raw": 2,
      "families_with_strict_raw": 1,
      "mean_motif_ca_rmsd": 1.2593830925803458
    }
  ],
  "elapsed_seconds": 128.43022884707898,
  "interpretation": "Reused development families and one post-selected case, with prospective fresh noise. This tests stochastic repeatability and conditional diversity, not independent-protein validation. No development refolds become training labels; locked tests remain unscored. Keep the failed fixed-panel and other recipe results intact. Views overlap by four samples perarm; raw matches require refolding."
}
```
