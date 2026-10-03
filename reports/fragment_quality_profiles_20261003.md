# Matched fragment-quality training

```json
{
  "status": "complete",
  "profile_only": true,
  "protocol_sha256": "13531e575d5c1ecc92a78b469273cf1ee1a7c3dbd9a066b2ecb7cec395732f42",
  "sources": [
    {
      "arm": "control",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50158806",
      "manifest_sha256": "ea46a7864938cef42d1204b584590effcc1f76d808e781df57041c4d68c574f5",
      "report_sha256": "b7785c80590ae029d4573d6032a153b093355f0c6a7d74f56e5ea54af4d83277"
    },
    {
      "arm": "quality",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50158938",
      "manifest_sha256": "7ea4ddaee39942b2c96a1e798f86bb0e13978ebe278c3e0b24bbf8ac7fc70d6b",
      "report_sha256": "1ca4cb9fce9ad66679b62cc92e713196abb1621cbf6b63ce3120f1c8883b9c8b"
    }
  ],
  "matched_training_updates": 40,
  "initial_predictions": {
    "control": 32,
    "quality": 32
  },
  "sampled_training_placement_counts": {
    "control": {
      "c20_right": 415,
      "c20_left": 402,
      "c20_center": 383
    },
    "quality": {
      "c20_left": 424,
      "c20_right": 391,
      "c20_center": 385
    }
  },
  "scope": "Same proteins, initial predictions, frozen generator, RNG and LR draws. Condition identity differs exactly as preregistered; corpus condition counts/lengths/placement margins match. Repeated sampled placement counts are reported separately and need not match exactly. Quality is not inferred from evaluation outcomes."
}
```
