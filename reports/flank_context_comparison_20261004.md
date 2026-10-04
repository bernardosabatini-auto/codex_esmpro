# Paired wider-context-mask geometry

```json
{
  "status": "complete",
  "source_report_sha256": "cc82d3e43458d14807c29005973bdb291700ad354b1e8dfe9089092535d15292",
  "baseline_report_sha256": "a3bbec38bbf862223683f71383c7f8fc2d47fe2a7169a237125ffccae18ab1b3",
  "summary": [
    {
      "model": "baseline",
      "arm": "generated_cond",
      "samples": 128,
      "complete_geometry": 30,
      "eligible_geometry": 30
    },
    {
      "model": "baseline",
      "arm": "generated_untrained",
      "samples": 128,
      "complete_geometry": 18,
      "eligible_geometry": 11
    },
    {
      "model": "flank",
      "arm": "generated_cond",
      "samples": 128,
      "complete_geometry": 0,
      "eligible_geometry": 0
    },
    {
      "model": "flank",
      "arm": "generated_untrained",
      "samples": 128,
      "complete_geometry": 0,
      "eligible_geometry": 0
    }
  ],
  "contrasts": [
    {
      "candidate": [
        "flank",
        "generated_cond"
      ],
      "reference": [
        "baseline",
        "generated_cond"
      ],
      "eligible_difference": {
        "mean": -0.234375,
        "ci95": [
          -0.3203125,
          -0.1484375
        ],
        "families": 32
      }
    },
    {
      "candidate": [
        "flank",
        "generated_cond"
      ],
      "reference": [
        "flank",
        "generated_untrained"
      ],
      "eligible_difference": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      }
    }
  ],
  "scope": "Same32training proteins x4noises; all outputs retained. Complete local geometry plus every peptide/CAedge in eight flanks. Family bootstrap. This is geometric feasibility, not designability or generalization."
}
```
