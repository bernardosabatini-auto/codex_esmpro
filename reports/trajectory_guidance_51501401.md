# Mid-flow decoder guidance pilot

Training-protein diagnostic. No designability claim. All outputs retained.

```json
{
  "status": "complete",
  "qualified": true,
  "designability_tested": false,
  "summary": {
    "baseline": {
      "samples": 16,
      "valid": 16,
      "raw": 3,
      "raw_families": 3,
      "mean_motif_rmsd": 2.119737115628963
    },
    "guided": {
      "samples": 16,
      "valid": 16,
      "raw": 15,
      "raw_families": 4,
      "mean_motif_rmsd": 0.5835986928175092
    }
  },
  "update_max_abs": 0.0,
  "batches": [
    {
      "arm": "baseline",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "samples": 4,
      "length": 113,
      "seconds": 0.7010384611785412,
      "recording_seconds": 0.027810397557914257,
      "peak_reserved_GiB": 2.1796875
    },
    {
      "arm": "guided",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "samples": 4,
      "length": 113,
      "seconds": 3.3428048491477966,
      "recording_seconds": 0.03575642500072718,
      "peak_reserved_GiB": 3.47265625
    },
    {
      "arm": "baseline",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "samples": 4,
      "length": 241,
      "seconds": 1.0825594696216285,
      "recording_seconds": 0.027470377273857594,
      "peak_reserved_GiB": 3.8828125
    },
    {
      "arm": "guided",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "samples": 4,
      "length": 241,
      "seconds": 3.645081751048565,
      "recording_seconds": 0.03833021968603134,
      "peak_reserved_GiB": 5.875
    },
    {
      "arm": "baseline",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "samples": 4,
      "length": 262,
      "seconds": 1.1343878018669784,
      "recording_seconds": 0.027302479837089777,
      "peak_reserved_GiB": 5.875
    },
    {
      "arm": "guided",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "samples": 4,
      "length": 262,
      "seconds": 3.8805439677089453,
      "recording_seconds": 0.036694195587188005,
      "peak_reserved_GiB": 6.5390625
    },
    {
      "arm": "baseline",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "samples": 4,
      "length": 486,
      "seconds": 2.3043011990375817,
      "recording_seconds": 0.06228970969095826,
      "peak_reserved_GiB": 9.078125
    },
    {
      "arm": "guided",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "samples": 4,
      "length": 486,
      "seconds": 7.99671567324549,
      "recording_seconds": 0.038016144186258316,
      "peak_reserved_GiB": 13.74609375
    }
  ],
  "elapsed_seconds": 46.499901096336544,
  "manifest_sha256": "3457d986994d881843e11d1153664636ac97025595c1e070fc58148dea55db32",
  "predictions_sha256": "b3a769c820e6b497dfec196ec7d188cb5e023530312636e5535d9a94ef87e889"
}
```
