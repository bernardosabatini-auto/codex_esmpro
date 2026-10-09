# Mid-flow guidance: same-refold verdict

```json
{
  "status": "complete",
  "qualified": false,
  "summary": {
    "native": {
      "samples": 4,
      "raw": 4,
      "strict": 3,
      "strict_families": 3,
      "designable": 3,
      "global_scaffold": 3,
      "connected_strict": 3
    },
    "baseline": {
      "samples": 16,
      "raw": 3,
      "strict": 1,
      "strict_families": 1,
      "designable": 4,
      "global_scaffold": 4,
      "connected_strict": 1
    },
    "guided": {
      "samples": 16,
      "raw": 10,
      "strict": 0,
      "strict_families": 0,
      "designable": 5,
      "global_scaffold": 5,
      "connected_strict": 0
    }
  },
  "gates": {
    "strict": false,
    "families": false,
    "designability": true,
    "native": true
  },
  "diversity": [
    {
      "arm": "baseline",
      "subset": "all",
      "pairs": 24,
      "families": 4,
      "mean_scaffold_tm": 0.16062583333333333,
      "mean_global_tm": 0.17511083333333333
    },
    {
      "arm": "baseline",
      "subset": "both_strict",
      "pairs": 0,
      "families": 0,
      "mean_scaffold_tm": null,
      "mean_global_tm": null
    },
    {
      "arm": "guided",
      "subset": "all",
      "pairs": 24,
      "families": 4,
      "mean_scaffold_tm": 0.15925999999999998,
      "mean_global_tm": 0.17661208333333334
    },
    {
      "arm": "guided",
      "subset": "both_strict",
      "pairs": 0,
      "families": 0,
      "mean_scaffold_tm": null,
      "mean_global_tm": null
    }
  ],
  "refold_report_sha256": "c788e685514bff951ddcbd4d9f4b84423922c20fa881062443ab70ae0c62c36a",
  "diversity_cache_sha256": "c2d0d3da2afd5b8efde5c3346d6f0c2d9e0294f49207588b895d56e5e807ad57",
  "new_refolds": 128,
  "reused_refolds": 160,
  "scope": "Four repeatedly used training families; fixed288refold budget. This is an inference-guidance pilot, not a newly trained model or independent benchmark. No historical sequence attempts pooled."
}
```
