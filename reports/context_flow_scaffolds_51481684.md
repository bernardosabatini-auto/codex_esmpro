# Context-code scaffold generation

The normalization correction did not rescue the learned context codes: both
learned arms remained 0/16 valid and 0/16 raw motif matches. Original and normalized
native-code controls both retained 14/16 valid motif matches; all eight numerical
control groups passed (worst normalized-native CA drift 0.0241 Å). The missing
projection was an interface oversight but does not explain this capacity failure.
This fixed context-code flow and its normalization correction are closed. No
larger correction assay, retraining extension, or refolding is justified.

The RTX allocation lasted 187 seconds; captured SM activity was 78.95%, with
40.77% weighted utilization over 61 seconds after initialization. All outputs and
failures are retained. The next CPU diagnostic checks actual training-fragment
coverage; it makes no designability claim.

```json
{
  "status": "complete",
  "qualified": false,
  "context_normalization_profile": true,
  "summary": {
    "oracle_original": {
      "samples": 16,
      "valid": 14,
      "raw": 14
    },
    "isolated": {
      "samples": 16,
      "valid": 0,
      "raw": 0
    },
    "ablated": {
      "samples": 16,
      "valid": 0,
      "raw": 0
    },
    "oracle_normalized": {
      "samples": 16,
      "valid": 14,
      "raw": 14
    },
    "isolated_unprojected": {
      "samples": 16,
      "valid": 0,
      "raw": 0
    },
    "ablated_unprojected": {
      "samples": 16,
      "valid": 0,
      "raw": 0
    }
  },
  "controls": [
    {
      "arm": "oracle_original",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.424572717598603e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_normalized",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0028841644525527954,
      "max_ca_rmsd": 0.011880575400023581,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_original",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 2.9429242907759805e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_normalized",
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "latent_max_abs": 0.000457763671875,
      "max_ca_rmsd": 0.001010498426423046,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_original",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.1487901746079594e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_normalized",
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "latent_max_abs": 0.0017847418785095215,
      "max_ca_rmsd": 0.003687386792600447,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_original",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 3.599987103443794e-14,
      "min_ca_lddt": 1.0,
      "same_decisions": true
    },
    {
      "arm": "oracle_normalized",
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "latent_max_abs": 0.01867622137069702,
      "max_ca_rmsd": 0.02409374644176821,
      "min_ca_lddt": 0.9999778604321643,
      "same_decisions": true
    }
  ],
  "manifest_sha256": "bfef2397f552a7a976c2f7422985d3e44fc317d504066bb8d0b219578379bf47",
  "predictions_sha256": "ad239111f96f354afdef00d5b0c2944706a49a6064bfc5637f94759e8c92e430",
  "elapsed_seconds": 151.5250756949972,
  "designability_tested": false
}
```
