# Training-only preference calibration

```json
{
  "status": "complete",
  "training_only": true,
  "protocol": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/configs/fragment_preference_calibration_protocol.json",
  "protocol_sha256": "a709e0625f7aa0c93bdfaf232e4b8e02f479deff7011388772f3013da4473aff",
  "generated": 128,
  "refolds": 1024,
  "native_budgets_reused": 32,
  "native_global_scaffold": 27,
  "raw_matches": 25,
  "strong": 8,
  "strong_families": 7,
  "designable": 45,
  "gate": {
    "qualified": false,
    "checks": {
      "coverage": false,
      "confirmation_rate": true,
      "length_buckets": true,
      "long_proteins": false,
      "native_calibration": true
    },
    "eligible": 8,
    "confirmed": 6,
    "confirmation_rate": 0.75
  },
  "by_length": [
    {
      "bucket": 128,
      "generated": 32,
      "strong": 3,
      "designable": 17
    },
    {
      "bucket": 256,
      "generated": 32,
      "strong": 4,
      "designable": 20
    },
    {
      "bucket": 384,
      "generated": 32,
      "strong": 1,
      "designable": 6
    },
    {
      "bucket": 512,
      "generated": 32,
      "strong": 0,
      "designable": 2
    }
  ],
  "decision": "Close this collection recipe; do not train on unqualified preferences or increase attempts/cutoff sweeps.",
  "scope": "Training-only label-feasibility collection, not model improvement. Strict1A success and graded2A preference feasibility are distinct. All128outputs retained; global/scaffold/motif evidence must share a valid refold."
}
```
