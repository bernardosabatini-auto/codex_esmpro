# Whole-chain scaffold-clock flow

```json
{
  "status": "complete",
  "scaffold_clock": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/scaffold_clock_training_50282184/manifest.json",
  "manifest_sha256": "938dfc36fa584b89fc8900412b0a2e07cdcc203608cf553de00398f1a8fce62b",
  "protocol_sha256": "64340c8708034fdee39c83cda42efcc32a9a47e99a13722a2417df21cc637036",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "d3fab8a7ad13fe3e6077cd4e9057e298a3b649caf4073a01f4da3b83f4282ea9",
  "predictions_sha256": "c97c3107f65252d3c754a62b86b7ce66bc9127c8992c810cdc5cdab0c6c3908d",
  "updates": 40,
  "trainable_parameters": 458738184,
  "training_seconds": 23.65577208204195,
  "elapsed_seconds": 123.1119978488423,
  "peak_reserved_GiB": 29.150390625,
  "controls": 16,
  "saved_ema_gpu_replay": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0
    }
  ],
  "initial_global_controls": 4,
  "prefix_max_abs": null,
  "recommended_full_minutes": 49,
  "summary": [
    {
      "arm": "parent",
      "samples": 16,
      "raw": 3,
      "valid": 16,
      "mean_motif_rmsd": 2.119737115628963,
      "mean_scaffold_rmsd": 1.6684304929436398e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "native_direct",
      "samples": 16,
      "raw": 16,
      "valid": 16,
      "mean_motif_rmsd": 0.08101941941320709,
      "mean_scaffold_rmsd": 8.900101825537118e-15,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "generated_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 2.296838613456748,
      "mean_scaffold_rmsd": 6.518049240449562,
      "mean_scaffold_lddt": 0.4253544272517126
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.4143855809553445,
      "mean_scaffold_rmsd": 6.452007219657201,
      "mean_scaffold_lddt": 0.4297745662012107
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 1.5122075120269245,
      "mean_scaffold_rmsd": 5.806368269059185,
      "mean_scaffold_lddt": 0.47159253635615794
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 3.894858394232723,
      "mean_scaffold_rmsd": 6.016272062421007,
      "mean_scaffold_lddt": 0.4589497884723765
    },
    {
      "arm": "initial_generated_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 2.204868532837466,
      "mean_scaffold_rmsd": 6.656680009125883,
      "mean_scaffold_lddt": 0.4207003387683925
    }
  ],
  "refold_gate": null,
  "contrasts": [],
  "scope": "Repeated training-only capacity diagnostic. Whole scaffold is free to move. Raw capacity does not establish same-refold designability. Native-context outputs are oracle controls; no model promotion."
}
```
