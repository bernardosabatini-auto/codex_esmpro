# Fragment noise replication

```json
{
  "status": "complete",
  "manifest_sha256": "16f04ea1a9d9e55ba80e68cc10c6281bcf473a9a497e1bbdd16105e22df54449",
  "predictions_sha256": "5c886eb374a278a0bf613b29989efb369073e02bcb2b51b6ee3e69f225604e6a",
  "summaries": [
    {
      "guidance": 1,
      "samples": 16,
      "valid": 16,
      "strict_raw": 3,
      "mean_motif_ca_rmsd": 1.4562372912380317,
      "raw_qualified_diversity_pairs": 3,
      "raw_qualified_scaffold_rmsd": 27.334591565107576
    },
    {
      "guidance": 2,
      "samples": 16,
      "valid": 16,
      "strict_raw": 1,
      "mean_motif_ca_rmsd": 1.309695648448908,
      "raw_qualified_diversity_pairs": 0,
      "raw_qualified_scaffold_rmsd": null
    }
  ],
  "controls": [
    {
      "kind": "historical",
      "guidance": 1,
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 4.041492112730146e-15,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "kind": "same_batch_repeat",
      "guidance": 1,
      "latent_max_abs": 0.0
    },
    {
      "kind": "historical",
      "guidance": 2,
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 9.076962366075818e-15,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "kind": "same_batch_repeat",
      "guidance": 2,
      "latent_max_abs": 0.0
    },
    {
      "kind": "pose",
      "guidance": 2,
      "latent_max_abs": 0.0
    }
  ],
  "timing": [
    {
      "guidance": 1,
      "seconds": 1.6388810509815812,
      "peak_reserved_GiB": 2.001953125
    },
    {
      "guidance": 2,
      "seconds": 3.1377075063064694,
      "peak_reserved_GiB": 2.017578125
    }
  ],
  "elapsed_seconds": 77.92496130708605,
  "interpretation": "Single selected development case, new fixed noise seed. Raw matches require refolding; this is not independent-protein validation."
}
```
