# Learned masked-fragment flow

```json
{
  "status": "complete",
  "profile_only": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/masked_fragment_training_50270326/manifest.json",
  "manifest_sha256": "774f0fdac1d24dfbaefcdeee2914d8848af97515902c5536a78d1ce5671a3962",
  "protocol_sha256": "f61e4614f41a62c4825eaa1af45c90d0b01f3b521c0cf83833d9c58222c55dd4",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "05cd2c44d92e0c760c60118f5f1a9d0550b63bd439af55d9b82de02315bbe2a7",
  "predictions_sha256": "a337b7dec0cfb291e0dc00434cfdafed7fcdbc3c3faa843d94f0e242921a20c1",
  "updates": 40,
  "trainable_parameters": 5080776,
  "training_seconds": 2.3839407418854535,
  "elapsed_seconds": 51.57755078934133,
  "peak_reserved_GiB": 5.6796875,
  "controls": 16,
  "saved_ema_cpu_replay": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 4.76837158203125e-07
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 5.960464477539062e-07
    }
  ],
  "prefix_max_abs": null,
  "recommended_full_minutes": 14,
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
      "mean_motif_rmsd": 66.2263527852644,
      "mean_scaffold_rmsd": 0.6421824568398712,
      "mean_scaffold_lddt": 0.973516275705561
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 66.2819325318494,
      "mean_scaffold_rmsd": 0.6420397013160727,
      "mean_scaffold_lddt": 0.9734981890503285
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 66.1750501373084,
      "mean_scaffold_rmsd": 0.8974318561269528,
      "mean_scaffold_lddt": 0.9582150599378417
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 66.23017493399475,
      "mean_scaffold_rmsd": 0.8971833454584741,
      "mean_scaffold_lddt": 0.9582698427101041
    }
  ],
  "refold_gate": null,
  "scope": "Repeated training-only capacity diagnostic. Exact latent scaffold retention does not imply fixed coordinates or same-refold designability. Native-context outputs are oracle controls; no model promotion."
}
```
