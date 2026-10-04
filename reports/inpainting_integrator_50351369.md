# Fixed-fragment integration diagnostic

```json
{
  "status": "complete",
  "manifest_sha256": "cfb46262f2d5b6201e6a7d4f6e27ec7b1cb30bec624c545f2b4db2dade6bbdc0",
  "predictions_sha256": "c775ef6c732d8ddb9b2ee21d959af1ea1310310cbdaf7f1c221f4079faad3b06",
  "controls": 104,
  "summary": [
    {
      "arm": "generated",
      "steps": 3,
      "samples": 128,
      "valid": 97,
      "junction_intact": 0,
      "connected_and_coarse": 0,
      "mean_junction_cn": 4.923619007691741
    },
    {
      "arm": "generated",
      "steps": 10,
      "samples": 128,
      "valid": 98,
      "junction_intact": 1,
      "connected_and_coarse": 1,
      "mean_junction_cn": 4.5369957943912596
    },
    {
      "arm": "native",
      "steps": 3,
      "samples": 128,
      "valid": 122,
      "junction_intact": 2,
      "connected_and_coarse": 2,
      "mean_junction_cn": 2.077597267460078
    },
    {
      "arm": "native",
      "steps": 10,
      "samples": 128,
      "valid": 128,
      "junction_intact": 6,
      "connected_and_coarse": 6,
      "mean_junction_cn": 1.9100751804653555
    }
  ],
  "path_summary": [
    {
      "arm": "trained",
      "t": 0,
      "samples": 128,
      "valid": 0,
      "junction_intact": 0,
      "connected_and_coarse": 0,
      "mean_junction_cn": 2.3998441048897803,
      "mean_unknown_ca_rmsd": 0.5403394801542163
    },
    {
      "arm": "trained",
      "t": 0.3333333333333333,
      "samples": 128,
      "valid": 75,
      "junction_intact": 1,
      "connected_and_coarse": 1,
      "mean_junction_cn": 2.2190023656003177,
      "mean_unknown_ca_rmsd": 0.21190628898330033
    },
    {
      "arm": "trained",
      "t": 0.6666666666666666,
      "samples": 128,
      "valid": 123,
      "junction_intact": 2,
      "connected_and_coarse": 2,
      "mean_junction_cn": 2.0494083864614367,
      "mean_unknown_ca_rmsd": 0.13531942147528753
    },
    {
      "arm": "trained",
      "t": 0.9,
      "samples": 128,
      "valid": 128,
      "junction_intact": 4,
      "connected_and_coarse": 4,
      "mean_junction_cn": 1.7850159285590053,
      "mean_unknown_ca_rmsd": 0.0866981988074258
    },
    {
      "arm": "original_unmasked",
      "t": 0,
      "samples": 128,
      "valid": 0,
      "junction_intact": 21,
      "connected_and_coarse": 0,
      "mean_junction_cn": 1.6911499942652881,
      "mean_unknown_ca_rmsd": 1.012655437225476
    },
    {
      "arm": "original_unmasked",
      "t": 0.3333333333333333,
      "samples": 128,
      "valid": 57,
      "junction_intact": 46,
      "connected_and_coarse": 23,
      "mean_junction_cn": 1.6083974078064784,
      "mean_unknown_ca_rmsd": 0.6151264184736647
    },
    {
      "arm": "original_unmasked",
      "t": 0.6666666666666666,
      "samples": 128,
      "valid": 125,
      "junction_intact": 62,
      "connected_and_coarse": 62,
      "mean_junction_cn": 1.532082068035379,
      "mean_unknown_ca_rmsd": 0.4567396398051642
    },
    {
      "arm": "original_unmasked",
      "t": 0.9,
      "samples": 128,
      "valid": 128,
      "junction_intact": 74,
      "connected_and_coarse": 74,
      "mean_junction_cn": 1.3893300713971257,
      "mean_unknown_ca_rmsd": 0.2162090215133503
    }
  ],
  "ten_step_followup_eligible": false,
  "elapsed_seconds": 68.07758768787608,
  "peak_reserved_GiB": 5.6796875,
  "scope": "Frozen training-only diagnostic. Motif coordinates are imposed. Oracle paths expose native endpoints and are not generation. No designability claim, refold pooling or parameter update."
}
```
