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
      "valid": 15,
      "raw": 10,
      "raw_families": 4,
      "mean_motif_rmsd": 1.006102581441247
    }
  },
  "update_max_abs": 0.0,
  "batches": [
    {
      "arm": "baseline",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "samples": 4,
      "length": 113,
      "seconds": 0.62868393631652,
      "recording_seconds": 0.02752452390268445,
      "peak_reserved_GiB": 3.478515625
    },
    {
      "arm": "guided",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "samples": 4,
      "length": 113,
      "seconds": 2.537095352075994,
      "recording_seconds": 0.036502948962152004,
      "peak_reserved_GiB": 3.740234375
    },
    {
      "arm": "baseline",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "samples": 4,
      "length": 241,
      "seconds": 1.0843257647939026,
      "recording_seconds": 0.027585722971707582,
      "peak_reserved_GiB": 5.908203125
    },
    {
      "arm": "guided",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "samples": 4,
      "length": 241,
      "seconds": 3.960446773096919,
      "recording_seconds": 0.035080903209745884,
      "peak_reserved_GiB": 6.318359375
    },
    {
      "arm": "baseline",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "samples": 4,
      "length": 262,
      "seconds": 1.1347857811488211,
      "recording_seconds": 0.027375351171940565,
      "peak_reserved_GiB": 6.572265625
    },
    {
      "arm": "guided",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "samples": 4,
      "length": 262,
      "seconds": 4.14794177794829,
      "recording_seconds": 0.03586659301072359,
      "peak_reserved_GiB": 7.060546875
    },
    {
      "arm": "baseline",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "samples": 4,
      "length": 486,
      "seconds": 2.277705913875252,
      "recording_seconds": 0.03451190935447812,
      "peak_reserved_GiB": 13.779296875
    },
    {
      "arm": "guided",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "samples": 4,
      "length": 486,
      "seconds": 8.694542387034744,
      "recording_seconds": 0.04008650593459606,
      "peak_reserved_GiB": 13.779296875
    }
  ],
  "elapsed_seconds": 62.538731982931495,
  "manifest_sha256": "8da31b8f8cee476fad8c0d126562df641e6d3c5f3086dbe3b216b6f9faf1bb62",
  "predictions_sha256": "49045ab01ebd8c9d32ccbd332282bc56c6ef07530843b8fad3dca3b0b9b56e59",
  "joint_sequence_guidance": true,
  "geometry_gate_passed": true,
  "sequence_nll": {
    "geometry": 3.172664538025856,
    "baseline": 3.1417879313230515,
    "guided": 2.501015529036522
  },
  "sequence_nll_improvement": 0.6716490089893341
}
```
