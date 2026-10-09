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
      "samples": 128,
      "valid": 86,
      "raw": 33
    },
    "random": {
      "samples": 128,
      "valid": 91,
      "raw": 1
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
  "full_panel": true,
  "refold_eligible": true,
  "reused_profile_samples": 48,
  "manifest_sha256": "d9630ad50f5a4892753b935659aea2284bbebb551f13b2202b06c6671783e93a",
  "predictions_sha256": "5b84a39d9e1a0d4ddaddd12282c1cb03905f7a7065edf551d18f0016b4d41a61",
  "elapsed_seconds": 203.50494060991332,
  "import_seconds": 10.007063002791256,
  "phases": {
    "cuda_and_telemetry_seconds": 0.6614683531224728,
    "local_staging_seconds": 1.3719254150055349,
    "generator_load_seconds": 1.4160599689930677,
    "decoder_load_seconds": 3.6682869610376656
  },
  "generation_seconds": 192.73565842211246,
  "peak_reserved_GiB": 6.794921875,
  "designability_tested": false
}
```
