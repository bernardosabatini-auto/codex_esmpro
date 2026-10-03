# Learned-generator freezing comparison

```json
{
  "status": "complete",
  "profile_only": true,
  "protocol_sha256": "635095807851f4d2c804c74708edad83947a51c1d73faeac950cfb092e57103c",
  "matched_training_updates": 40,
  "initial_predictions": {
    "control_frozen": 32,
    "broad_frozen": 32
  },
  "sources": [
    {
      "arm": "control_frozen",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50138273",
      "manifest_sha256": "12affb3b79213fff2f62650e72730c35fe5891eab958282af7b44f4bd740fa58",
      "report_sha256": "fbfdb42876018693766865d69501f5ac986824183adef17e8d05392cf0f422d9"
    },
    {
      "arm": "broad_frozen",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50138469",
      "manifest_sha256": "881fcba40df141c783233f8cb681a9ef7a32496a8f3419b93d98e3bf97c5c76d",
      "report_sha256": "77217629a574c295dcdbc7e30a21ac5694e47dfa6fa7d913ae14c69502d4ff80"
    },
    {
      "arm": "control_weight3",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50126352",
      "manifest_sha256": "20a3db6b0ba226c837ca2669cde5ee96d2e6b8a913d18276821c175ee1e18d06",
      "report_sha256": "c26a3e9a5b831765612e469f0315ca3bee3e8dba23304398d1104d7fc444c4e6"
    },
    {
      "arm": "broad_weight3",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50126512",
      "manifest_sha256": "a1f95bddf13dd7771ae9c04ea407b8c73a2a6f37dc0b5522b369826ef6edd663",
      "report_sha256": "13b99d1ea3fc35cf5569082332dc995369276167c4a0aa3bf1104c5e39a54eff"
    }
  ],
  "scope": "Only fragment adapters update in the new arms. Reused full-network controls retain original reports and budgets. Initial outputs, training exposure and RNG traces must match."
}
```
