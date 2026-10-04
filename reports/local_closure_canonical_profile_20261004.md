# Local backbone closure

```json
{
  "status": "complete",
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/local_closure_canonical_profile_20261004/manifest.json",
  "manifest_sha256": "41e95f2f7598b4afee52c05b6a5f8d377e530d6dc1e442d4878209629adf8441",
  "predictions_sha256": "fc787154c77c722853fb5c87ba6610f224487429c99869f6d800062dc95b4f85",
  "protocol_sha256": "56b64d5f3be6cb33526ac2e2491652396be06f4bfb3df9b0b7a1adda8681a470",
  "elapsed_seconds": 34.13407266209833,
  "estimated_full_seconds": 422,
  "controls": 20,
  "prefix_max_abs": null,
  "summary": [
    {
      "arm": "generated_cond",
      "samples": 16,
      "coarse_valid": 16,
      "connected_raw": 16,
      "qualified_raw": 5,
      "local_geometry": 5,
      "mean_max_atom_displacement": 5.406247816979885
    },
    {
      "arm": "generated_untrained",
      "samples": 16,
      "coarse_valid": 12,
      "connected_raw": 12,
      "qualified_raw": 3,
      "local_geometry": 4,
      "mean_max_atom_displacement": 7.549653023481369
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "coarse_valid": 16,
      "connected_raw": 16,
      "qualified_raw": 16,
      "local_geometry": 16,
      "mean_max_atom_displacement": 0.8175450824201107
    }
  ],
  "scope": "CPU-only local closure; fixed motif and far scaffold, generated-parent geometry targets. Native arm explicitly oracle. All failures retained. Geometric feasibility alone does not establish designability or same-refold motif/global/scaffold agreement."
}
```
