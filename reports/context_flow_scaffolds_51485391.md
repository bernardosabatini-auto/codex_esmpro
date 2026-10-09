# Context-code scaffold generation

```json
{
  "status": "complete",
  "qualified": true,
  "retrieved_context_profile": true,
  "summary": {
    "oracle_original": {
      "samples": 16,
      "valid": 14,
      "raw": 14
    },
    "retrieved": {
      "samples": 16,
      "valid": 9,
      "raw": 6
    },
    "random": {
      "samples": 16,
      "valid": 11,
      "raw": 0
    },
    "donor_self": {
      "samples": 16,
      "valid": 12,
      "raw": 12
    }
  },
  "controls": [
    {
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.424572717598603e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 2.9429242907759805e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.1487901746079594e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 3.599987103443794e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    }
  ],
  "manifest_sha256": "9e3c647bfcec6b4c85044e269f42777d844682bbba8a3d1f4287725783be0adf",
  "predictions_sha256": "19e6f5c6570fefd37901392bc599981fb5c62dfb16c85b97c6a6f461e56079a8",
  "elapsed_seconds": 118.44804830197245,
  "import_seconds": 9.144884642213583,
  "phases": {
    "cuda_and_telemetry_seconds": 0.6204097177833319,
    "local_staging_seconds": 3.0356340701691806,
    "generator_load_seconds": 1.3527998994104564,
    "decoder_load_seconds": 56.88225490460172
  },
  "generation_seconds": 55.41402237024158,
  "peak_reserved_GiB": 6.818359375,
  "designability_tested": false
}
```
