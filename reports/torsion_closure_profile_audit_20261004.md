# Independent torsion-closure audit

```json
{
  "status": "complete",
  "qualified": true,
  "profile_only": true,
  "samples": 32,
  "source_report_sha256": "6368c2a174b35150cf7b1e4a76564a87c58f941bb195ddb40a616bf3caa412d2",
  "predictions_sha256": "60c77b793d4c3b1bd7dc21e9bed219404aa842f3e77b18c599a72be39d9c17bd",
  "max_replay_angstrom": 0.0,
  "max_endpoint_replay_angstrom": 0.0,
  "summary": [
    {
      "arm": "generated_cond",
      "samples": 16,
      "coarse_valid": 14,
      "local_geometry": 12,
      "all_flank_edges_valid": 14,
      "eligible": 12
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "coarse_valid": 16,
      "local_geometry": 16,
      "all_flank_edges_valid": 16,
      "eligible": 16
    }
  ],
  "scope": "Every unfiltered saved output replayed from its stored torsions and rescored for actual assembled geometry. Constructive feasibility only; no learned or refolded success claim."
}
```
