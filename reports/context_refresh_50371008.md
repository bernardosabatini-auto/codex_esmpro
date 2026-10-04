# Whole-scaffold context refresh

```json
{
  "profile_only": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/context_refresh_50371008/manifest.json",
  "manifest_sha256": "15aa0ad0b605afda13ef1f73ea24f29f2b98d47a7e921633acf029a8c20296ec",
  "protocol_sha256": "073e386239d7c191083da00a087ac5fe46466ec6a28135adb75bf04a206704cc",
  "status": "complete",
  "qualified": true,
  "numerically_qualified": true,
  "summary": [
    {
      "arm": "trained",
      "round": 1,
      "samples": 16,
      "raw_coarse": 12,
      "raw_connected": 0,
      "raw_complete": 0,
      "closed_coarse": 14,
      "closed_connected": 14,
      "closed_complete": 5,
      "mean_scaffold_ca_displacement": 0.14028442278504372
    },
    {
      "arm": "trained",
      "round": 3,
      "samples": 16,
      "raw_coarse": 0,
      "raw_connected": 0,
      "raw_complete": 0,
      "closed_coarse": 1,
      "closed_connected": 1,
      "closed_complete": 0,
      "mean_scaffold_ca_displacement": 0.4110186640173197
    },
    {
      "arm": "untrained",
      "round": 1,
      "samples": 16,
      "raw_coarse": 11,
      "raw_connected": 0,
      "raw_complete": 0,
      "closed_coarse": 11,
      "closed_connected": 11,
      "closed_complete": 3,
      "mean_scaffold_ca_displacement": 0.3259996073320508
    },
    {
      "arm": "untrained",
      "round": 3,
      "samples": 16,
      "raw_coarse": 1,
      "raw_connected": 0,
      "raw_complete": 0,
      "closed_coarse": 4,
      "closed_connected": 4,
      "closed_complete": 1,
      "mean_scaffold_ca_displacement": 1.1598588824272156
    }
  ],
  "controls": 32,
  "predictions_sha256": "8618281c5c6179cdad3c97f8ecd000d7c11222efc38fae758fee8a84e29d40b2",
  "closed_sha256": "7ce7556a04d1f1ebe6fcd48a4ce62dc211bedd8220c4afe0a8a6758331423320",
  "prefix_max_abs": null,
  "gpu_elapsed_seconds": 37.22115063294768,
  "peak_reserved_GiB": 5.703125,
  "cpu_closure_seconds": 37.233303256798536,
  "estimated_full_gpu_seconds": 507,
  "estimated_full_cpu_seconds": 507,
  "scope": "Frozen three-pass whole-context refresh on ORIGINAL desired fragments. All training-diagnostic outputs retained. Round1 explanatory only; only round3 can qualify full128x8refolds. Geometry does not establish designability. Costs exclude historical cached starts."
}
```

The profile passes its numerical/runtime prerequisite but the scientific candidate
is abandoned before full-panel expansion. Trained round3has0/16coarse-valid raw
outputs and0/16complete geometry passes after closure. The starting trained
backbones were16/16coarse-valid. Round1has5/16complete closures, exactly the old
starting profile count; it is not substituted for the prespecified round3endpoint.

Independent CPU localization finds bad peptide bonds outside the motif/flank region
rising19→62→154→283over the original3,928far bonds across rounds0→1→2→3. The loop
accumulates errors across the scaffold rather than resolving the imposed motif
conflict. These are four-protein feasibility results, not a full128sample estimate.
No full-panel GPU job or refold assay is submitted. Both models and every failure
remain archived. The qualified flag in the machine report means technical
profile qualification only; it is not a scientific promotion.
