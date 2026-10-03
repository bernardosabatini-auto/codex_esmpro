# Training-only preference calibration

```json
{
  "status": "complete",
  "training_only": true,
  "protocol": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/configs/native_anchor_calibration_protocol.json",
  "protocol_sha256": "27c7993d570d8d2195a79fe4bd3b216d66bea8ef2ebacf108213f87bf466c5e5",
  "generation_manifest_sha256": "2f624189b2be68059d76a774560f94ce6633bc20532081817bfb703eee24f20e",
  "generated": 64,
  "native_decodes": 32,
  "refolds": 768,
  "native_budgets_reused": 16,
  "native_global_scaffold": 15,
  "summary": [
    {
      "arm": "parent6000",
      "samples": 64,
      "raw_matches": 6,
      "strong": 0,
      "designable": 22
    },
    {
      "arm": "native_latent",
      "samples": 32,
      "raw_matches": 32,
      "strong": 22,
      "designable": 30
    }
  ],
  "native_both_strict": 10,
  "gate": {
    "qualified": true,
    "checks": {
      "coverage": true,
      "confirmation_rate": true,
      "length_buckets": true,
      "long_proteins": true,
      "native_calibration": true,
      "native_both_strict": true
    },
    "eligible": 12,
    "confirmed": 10,
    "confirmation_rate": 0.8333333333333334
  },
  "decision": "Preregister positive-only versus bounded reference-anchored contrastive training.",
  "scope": "Disjoint training-only native-latent qualification. Both native decoder realizations must separately satisfy strict same-refold criteria and full-native roundtrip<=1A. Native attempts are never pooled. Previous generated-only gate remains failed. No generalization claim."
}
```
