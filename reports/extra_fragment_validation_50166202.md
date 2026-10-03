# Additional-family conditional generation

```json
{
  "status": "complete",
  "arm": "control",
  "manifest_sha256": "57c11ce8e3ba16067936e82281a8938df1666d106de9ef52af7363975693a051",
  "predictions_sha256": "8661dc9c9486d526b0dc5c78d0f5dff3817af07922eaa69ab60331cffe44bc1a",
  "summaries": [
    {
      "cohort": "all",
      "samples": 256,
      "families": 64,
      "valid": 251,
      "raw_matches": 34,
      "mean_motif_ca_rmsd": 2.5032414487059937
    },
    {
      "cohort": "short",
      "samples": 128,
      "families": 32,
      "valid": 124,
      "raw_matches": 22,
      "mean_motif_ca_rmsd": 2.3180580061360576
    },
    {
      "cohort": "long",
      "samples": 128,
      "families": 32,
      "valid": 127,
      "raw_matches": 12,
      "mean_motif_ca_rmsd": 2.68842489127593
    }
  ],
  "controls": 132,
  "elapsed_seconds": 233.57337119895965,
  "scope": "Repeated64-family development comparison. Training-condition quality alone differs between new arms; teacher-kernel policy is shared. No evaluation labels train either model. The6000parent and original native attempts are historical references, not new pooled budgets. Raw retention does not establish designability."
}
```
