# Dynamic fragment routing audit

```json
{
  "status": "complete",
  "profile_only": false,
  "protocol_sha256": "96e3e5b0553c3b6be4e9855d40d93e840de34306939ad273b54cc00f2dc5ff8c",
  "matched_training_updates": 2000,
  "initial_predictions": {
    "motif": 384,
    "all": 384
  },
  "sources": [
    {
      "arm": "motif",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50171694",
      "manifest_sha256": "5dfc6cd29d20dfe2482bd3b0e318867804c283ce4f73dc748da3d5cd02d00cc7",
      "report_sha256": "77b411918ab717c7278ff0e8082c347155b379451cdc169dbc9772b354c707c3"
    },
    {
      "arm": "all",
      "run": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_training_50171768",
      "manifest_sha256": "dae067f5625f139d173a0daf9181004be7d019eaa1cb7b6a31030641f2740d36",
      "report_sha256": "3006c65aa9bf4b154f23aa59c425156dc90831cf15237545f65c86d46f797fda"
    }
  ],
  "scope": "Same frozen6000parent and adapter; equal new parameters, memory and random draws. Only cross-attention output routing differs. Technical checks do not establish designability."
}
```
