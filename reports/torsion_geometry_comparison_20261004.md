# Matched physical-feasibility comparison

```json
{
  "status": "complete",
  "source_report_sha256": "18dced564834de25b4f33a7d85c870c490078265f666191ccd697fe68f8815bc",
  "audit_report_sha256": "27b7045a2c6feb44f03ab2c5fb97c5e99665cd3deecac2c8d66e32eb8da3d066",
  "baseline_report_sha256": "a3bbec38bbf862223683f71383c7f8fc2d47fe2a7169a237125ffccae18ab1b3",
  "summary": [
    {
      "arm": "generated_cond",
      "model": "cartesian_then_four_residue_closure",
      "samples": 128,
      "eligible": 0
    },
    {
      "arm": "generated_cond",
      "model": "torsion_closure",
      "samples": 128,
      "eligible": 61
    },
    {
      "arm": "native_cond",
      "model": "cartesian_then_four_residue_closure",
      "samples": 128,
      "eligible": 0
    },
    {
      "arm": "native_cond",
      "model": "torsion_closure",
      "samples": 128,
      "eligible": 124
    }
  ],
  "contrasts": [
    {
      "arm": "generated_cond",
      "eligible_difference": {
        "mean": 0.4765625,
        "ci95": [
          0.3671875,
          0.5859375
        ],
        "families": 32
      }
    },
    {
      "arm": "native_cond",
      "eligible_difference": {
        "mean": 0.96875,
        "ci95": [
          0.90625,
          1.0
        ],
        "families": 32
      }
    }
  ],
  "scope": "All128cases per arm, same originals/fragments/noises. BOTH methods rescored for complete geometry across eight flanks. The old four-residue recipe/results remain unchanged. Multiple aspects of these constructions differ; this is not a learned-model ablation or designability/generalization evidence."
}
```
