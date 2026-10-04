# Explicit fragment-conditioned coordinate decoder

```json
{
  "status": "complete",
  "fragment_decoder": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_decoder_training_50293210/manifest.json",
  "manifest_sha256": "2123692a610552840040aa5c0fab6c0474f21b692d88cfb66b763f6a12ba9f1e",
  "protocol_sha256": "3441d5c292c095672e8975ce8aa5ee4f25feb36464a5fa96498c2876e94c86bb",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "fcb2679ca55a0d4656f7ab0ff3117f0b471af600ac02ad117bd89ad81de273a0",
  "predictions_sha256": "467a8e849c7d2372116a4d86c2527e01ee1401e0b6fef4a9575cbc7bf25573cf",
  "updates": 2000,
  "trainable_parameters": 82944,
  "training_seconds": 806.5290455562063,
  "elapsed_seconds": 871.2527025477029,
  "peak_reserved_GiB": 8.54296875,
  "controls": 192,
  "initial_controls": 72,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      180.27459716796875,
      180.27459716796875
    ],
    "token_gradient_norm": 2.9071974754333496,
    "pair_gradient_norm": 6.739734172821045,
    "prediction_tolerance_ratio": 0.0,
    "gradient_tolerance_ratio": 0.0
  },
  "saved_ema_gpu_replay": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "backbone_max_abs": 0.0
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "backbone_max_abs": 0.0
    }
  ],
  "prefix_max_abs": 0.0,
  "recommended_full_minutes": null,
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "raw": 25,
      "valid": 128,
      "mean_motif_rmsd": 2.251629539928018,
      "mean_scaffold_rmsd": 9.705273561587831e-15
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.4424526297461972e-14
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.454398258031221,
      "mean_scaffold_rmsd": 0.2826395552250359
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.590508217676255,
      "mean_scaffold_rmsd": 0.3739366244091183
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 6.373555559958842,
      "mean_scaffold_rmsd": 0.38234367629398625
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 10.596421132691903,
      "mean_scaffold_rmsd": 0.4751421808557237
    }
  ],
  "refold_eligibility": {
    "qualified": false,
    "checks": {
      "strict_success_still_possible": false,
      "designability_floor_still_possible": false
    },
    "scope": "Logical feasibility only. Actual same-valid-refold success and designability decide advancement."
  },
  "contrasts": [
    {
      "candidate": "generated_cond",
      "reference": "parent",
      "metrics": {
        "raw_gate_passed": {
          "mean": -0.1953125,
          "ci95": [
            -0.28125,
            -0.1171875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -1.0,
          "ci95": [
            -1.0,
            -1.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 4.202768718103202,
          "ci95": [
            3.7966967678566985,
            4.6309496406828465
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "generated_cond",
      "reference": "generated_null",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -4.136109959645037,
          "ci95": [
            -4.514909073403911,
            -3.7656044185093536
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "native_cond",
      "reference": "native_null",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -4.222865572733061,
          "ci95": [
            -4.743776341102036,
            -3.7227173236977067
          ],
          "families": 32
        }
      }
    }
  ],
  "scope": "Repeated training-only diagnostic. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement."
}
```
