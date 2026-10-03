# Learned-generator freezing comparison

```json
{
  "status": "complete",
  "profile_only": false,
  "protocol_sha256": "635095807851f4d2c804c74708edad83947a51c1d73faeac950cfb092e57103c",
  "matched_training_updates": 2000,
  "initial_predictions": {
    "control_frozen": 384,
    "broad_frozen": 384
  },
  "sources": [
    {
      "arm": "control_frozen",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50139079",
      "manifest_sha256": "53564094b5d0a0be93c9fd4bcc70857a960d976ee4212eef4c203cdc8837f001",
      "report_sha256": "08c17b06397cba876480926e47b9cab5536f82ee0285410daf89cbf9a58a5572"
    },
    {
      "arm": "broad_frozen",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50139147",
      "manifest_sha256": "d28d0bf1c81f3f478c921e9e2f82b3a04721a8b963f2d041ab576312b00d168c",
      "report_sha256": "011e3ff7adbefbb19306c2ae5dd54916aea8217ef4837281774c92700885b2aa"
    },
    {
      "arm": "control_weight3",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50127267",
      "manifest_sha256": "36a9197640a1d5f7f8820ea86cee8654ccf8640b7232a7e6380ac64bc3ba2915",
      "report_sha256": "bfdd5de619597cb020337990a410ff12fe8c30ce10a282ed73923375b3d5a5bb"
    },
    {
      "arm": "broad_weight3",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50127352",
      "manifest_sha256": "361ebc5c40259dfffe3cdc182a632f9bc62ef6f5f83eab3051a60df262e2d365",
      "report_sha256": "ee0aa1482c86c35d2b424139c651da7fca9973aaf36c938dc67c9e8478d01bd4"
    }
  ],
  "scope": "Only fragment adapters update in the new arms. Reused full-network controls retain original reports and budgets. Initial outputs, training exposure and RNG traces must match."
}
```
