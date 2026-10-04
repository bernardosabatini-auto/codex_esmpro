# Independent torsion-closure audit

```json
{
  "status": "complete",
  "qualified": true,
  "profile_only": false,
  "samples": 256,
  "source_report_sha256": "18dced564834de25b4f33a7d85c870c490078265f666191ccd697fe68f8815bc",
  "predictions_sha256": "ace4159e7a323e7df9b91b0ceaf6035a8f34096ef6eceecf50ca98eedc02c0cd",
  "max_replay_angstrom": 0.0,
  "max_endpoint_replay_angstrom": 0.0,
  "summary": [
    {
      "arm": "generated_cond",
      "samples": 128,
      "coarse_valid": 74,
      "local_geometry": 101,
      "all_flank_edges_valid": 111,
      "eligible": 61
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "coarse_valid": 128,
      "local_geometry": 128,
      "all_flank_edges_valid": 124,
      "eligible": 124
    }
  ],
  "scope": "Every unfiltered saved output replayed from its stored torsions and rescored for actual assembled geometry. Constructive feasibility only; no learned or refolded success claim."
}
```
