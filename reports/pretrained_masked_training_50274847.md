# Pretrained masked-fragment flow

```json
{
  "status": "complete",
  "pretrained_masked": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/pretrained_masked_training_50274847/manifest.json",
  "manifest_sha256": "7d245d814da22ff241a6c9e8d5991dc8d2addb983f73ccc82a784cd62eac2772",
  "protocol_sha256": "85f9933578677f4f9bd7edf6bd82709d771c934c6a4d2ddd758ee0699bbd6a09",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "c8bc182be6947c152ec05823de70e231f10ab5647c8164e103ce6651ed275f51",
  "predictions_sha256": "efb5d6350d70cfda415cbcd97a62067b7fac0ed2b8b58a1df053c89c516a4938",
  "updates": 2000,
  "trainable_parameters": 458739976,
  "training_seconds": 1165.882040840108,
  "elapsed_seconds": 1462.9920507511124,
  "peak_reserved_GiB": 29.171875,
  "controls": 128,
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
  "prefix_max_abs": 2.798810601234436e-05,
  "recommended_full_minutes": null,
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "raw": 25,
      "valid": 128,
      "mean_motif_rmsd": 2.251629539928018,
      "mean_scaffold_rmsd": 1.2388032569484769e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.1961144712089116e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 25,
      "valid": 122,
      "mean_motif_rmsd": 2.3528782336543363,
      "mean_scaffold_rmsd": 0.0692579151291248,
      "mean_scaffold_lddt": 0.9990672594833794
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 7,
      "valid": 119,
      "mean_motif_rmsd": 4.915001771731923,
      "mean_scaffold_rmsd": 0.08131576510357238,
      "mean_scaffold_lddt": 0.9988592970328775
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 81,
      "valid": 124,
      "mean_motif_rmsd": 1.3241141513261376,
      "mean_scaffold_rmsd": 0.0406898118413091,
      "mean_scaffold_lddt": 0.9997929352549362
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 29,
      "valid": 126,
      "mean_motif_rmsd": 3.4249888640189483,
      "mean_scaffold_rmsd": 0.059740942982715595,
      "mean_scaffold_lddt": 0.9993113580904275
    }
  ],
  "refold_gate": {
    "qualified": false,
    "checks": {
      "native_capacity": false,
      "native_validity": false,
      "generated_validity": false,
      "raw_gain_over_parent": false,
      "raw_gain_over_null": true,
      "families": true
    },
    "improved_families": 5
  },
  "scope": "Repeated training-only capacity diagnostic. Exact latent scaffold retention does not imply fixed coordinates or same-refold designability. Native-context outputs are oracle controls; no model promotion."
}
```
