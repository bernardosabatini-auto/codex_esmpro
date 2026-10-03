# Native-positive coverage qualification

```json
{
  "status": "complete",
  "protocol": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/configs/native_positive_coverage_protocol.json",
  "protocol_sha256": "1dbd810313a1aa6cced9b868f563cb00a847d523cd2293bbb20294d8f5e690b2",
  "generation_manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/native_positive_decode_50239795/manifest.json",
  "generation_manifest_sha256": "2d63e87aba9e32db7e09045be56ae0bd3d6df32e38e36f3d422fe556bda43d72",
  "generation_report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/native_positive_decode_50239795.json",
  "generation_report_sha256": "752077324ca5e5bc6feca1799805282eeb39a94d62d812a60760d0b327fd9f42",
  "proteins": 64,
  "decoded_backbones": 128,
  "refolds": 1024,
  "raw_both_qualified": 60,
  "gate": {
    "qualified": true,
    "checks": {
      "coverage": true,
      "buckets": true,
      "long": true
    },
    "new_qualified": 42,
    "new_long_qualified": 24,
    "buckets": 4
  },
  "strong_decodes": 87,
  "designable_decodes": 110,
  "by_length": [
    {
      "bucket": 128,
      "proteins": 8,
      "qualified": 5
    },
    {
      "bucket": 256,
      "proteins": 16,
      "qualified": 13
    },
    {
      "bucket": 384,
      "proteins": 20,
      "qualified": 12
    },
    {
      "bucket": 512,
      "proteins": 20,
      "qualified": 12
    }
  ],
  "scope": "Training-source reference-positive qualification only. Both decoder realizations must separately pass strict raw/full-reference and same-valid-refold motif/global/scaffold criteria. No pooling, outcome-based source selection, or model improvement claim."
}
```
