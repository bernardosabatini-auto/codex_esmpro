# Dynamic fragment routing audit

```json
{
  "status": "complete",
  "profile_only": true,
  "protocol_sha256": "96e3e5b0553c3b6be4e9855d40d93e840de34306939ad273b54cc00f2dc5ff8c",
  "matched_training_updates": 40,
  "initial_predictions": {
    "motif": 32,
    "all": 32
  },
  "sources": [
    {
      "arm": "motif",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50171235",
      "manifest_sha256": "bf34b9cb9e2f056c9dd0caa625d9dce7116181f56f778e9500ffc568f84c1fee",
      "report_sha256": "72f45c3a63cb158797aa6fc63a6d78d747bbc213eb10b2fcb26d2c6244e99ec1"
    },
    {
      "arm": "all",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50171295",
      "manifest_sha256": "4a7a192f26db635eda27a67861b1923f581af7070b0f4b75f3b001981fc686f8",
      "report_sha256": "91e0a47b12c6a920b9aaadc1377ba94d8d82ad55e481fd733d881d6b49123875"
    }
  ],
  "scope": "Same frozen6000parent and adapter; equal new parameters, memory and random draws. Only cross-attention output routing differs. Technical checks do not establish designability."
}
```
