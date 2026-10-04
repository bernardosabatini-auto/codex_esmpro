# Paired context-conditioned scaffold geometry

```json
{
  "status": "complete",
  "candidate": "bridge",
  "source_report_sha256": "d6b769b04f62c606e7c90c0c232167ae15cbfb573db5ee766d45e6fa2ff9403d",
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
      "model": "bridge",
      "arm": "generated_cond",
      "samples": 128,
      "complete_geometry": 1,
      "eligible_geometry": 0
    },
    {
      "model": "bridge",
      "arm": "generated_untrained",
      "samples": 128,
      "complete_geometry": 0,
      "eligible_geometry": 0
    }
  ],
  "contrasts": [
    {
      "candidate": [
        "bridge",
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
        "bridge",
        "generated_cond"
      ],
      "reference": [
        "bridge",
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
