# Pretrained masked-fragment flow

```json
{
  "status": "complete",
  "pretrained_masked": true,
  "profile_only": true,
  "numerically_qualified": true,
  "qualified": true,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/pretrained_masked_training_50273620/manifest.json",
  "manifest_sha256": "402aa603ea9e6ac9a8330dd60022644916a7f839881840bbe1d6198d6fba66ac",
  "protocol_sha256": "85f9933578677f4f9bd7edf6bd82709d771c934c6a4d2ddd758ee0699bbd6a09",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "085ace13ef3d5f55cb065de5dad93e90f4d0ca2e706f304f026e273486e56be7",
  "predictions_sha256": "4af5e8ad826ef9be1c74d1fc86ec836fbd3f280229a8c70946c26b747db96548",
  "updates": 40,
  "trainable_parameters": 458739976,
  "training_seconds": 24.091619248036295,
  "elapsed_seconds": 120.12361517781392,
  "peak_reserved_GiB": 29.169921875,
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
      "raw": 2,
      "valid": 15,
      "mean_motif_rmsd": 2.517067287664062,
      "mean_scaffold_rmsd": 0.07903866791233566,
      "mean_scaffold_lddt": 0.9989202815539877
    },
    {
      "arm": "generated_null",
      "samples": 16,
      "raw": 1,
      "valid": 12,
      "mean_motif_rmsd": 4.931726190042983,
      "mean_scaffold_rmsd": 0.10504800126485686,
      "mean_scaffold_lddt": 0.9981557771598484
    },
    {
      "arm": "native_cond",
      "samples": 16,
      "raw": 8,
      "valid": 15,
      "mean_motif_rmsd": 1.7578124604971266,
      "mean_scaffold_rmsd": 0.06179048122915443,
      "mean_scaffold_lddt": 0.9991851468673105
    },
    {
      "arm": "native_null",
      "samples": 16,
      "raw": 2,
      "valid": 15,
      "mean_motif_rmsd": 3.244468488527286,
      "mean_scaffold_rmsd": 0.08067369057268305,
      "mean_scaffold_lddt": 0.9982533568949183
    }
  ],
  "refold_gate": null,
  "scope": "Repeated training-only capacity diagnostic. Exact latent scaffold retention does not imply fixed coordinates or same-refold designability. Native-context outputs are oracle controls; no model promotion."
}
```
