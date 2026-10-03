# Matched fragment-quality training

```json
{
  "status": "complete",
  "profile_only": false,
  "protocol_sha256": "13531e575d5c1ecc92a78b469273cf1ee1a7c3dbd9a066b2ecb7cec395732f42",
  "sources": [
    {
      "arm": "control",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50162221",
      "manifest_sha256": "96862191d1edf2169feeb55329cb17586ad4639a6ccbcd69e37ff95e62c7836e",
      "report_sha256": "3874ad8d0c19a3e9101d683952b12b8b208567a26c0d449c521f3c52df4d69af"
    },
    {
      "arm": "quality",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50162404",
      "manifest_sha256": "a7a65f4004a3f991a141352e7bc46f2412257bc284061090715a33d022b5b3b6",
      "report_sha256": "af59d42492eca81b5464b103d121eeac24f5e1a1f86ac956dfe8033f04947f4e"
    }
  ],
  "matched_training_updates": 2000,
  "initial_predictions": {
    "control": 384,
    "quality": 384
  },
  "sampled_training_placement_counts": {
    "control": {
      "c20_right": 19991,
      "c20_left": 19910,
      "c20_center": 20099
    },
    "quality": {
      "c20_left": 20025,
      "c20_right": 19969,
      "c20_center": 20006
    }
  },
  "scope": "Same proteins, initial predictions, frozen generator, RNG and LR draws. Condition identity differs exactly as preregistered; corpus condition counts/lengths/placement margins match. Repeated sampled placement counts are reported separately and need not match exactly. Quality is not inferred from evaluation outcomes."
}
```
