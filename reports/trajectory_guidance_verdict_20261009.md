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
      "raw": 15,
      "strict": 0,
      "strict_families": 0,
      "designable": 4,
      "global_scaffold": 4,
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
      "mean_scaffold_tm": 0.16172791666666667,
      "mean_global_tm": 0.18397750000000002
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
  "refold_report_sha256": "7339d7cf339d7c1886b1555f618380f69312b8c480da103841bb40275a553ceb",
  "diversity_cache_sha256": "584824fd3436b2216b9eb754225b0d9eaa8af0e920d797fe10cc4653fbe340ac",
  "scope": "Four repeatedly used training families; fixed288refold budget. This is an inference-guidance pilot, not a newly trained model or independent benchmark. No historical sequence attempts pooled."
}
```
