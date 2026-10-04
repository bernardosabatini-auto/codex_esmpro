# Full fragment-conditioned decoder denoising

```json
{
  "status": "complete",
  "fragment_decoder_fm": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_decoder_fm_training_50301053/manifest.json",
  "manifest_sha256": "5f1a29cd95d73039f4adc385bc4024f21b5937bdf0404c01c16a75af265b3ad8",
  "protocol_sha256": "9536ab9ff171d0713106809d678f2696ba121b09076e4eda719a5e3d45085717",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "02e53a28fefe42ad68baeb83d6c5bae90732ba15b7dec13bf98b520221d5d8dd",
  "predictions_sha256": "00772d166993d212e14879ed6e01c1a24bec00b80bbfb52596ab7cbb6a2fdc64",
  "updates": 2000,
  "trainable_parameters": 9316304,
  "training_seconds": 697.8592594265938,
  "elapsed_seconds": 769.5776891107671,
  "peak_reserved_GiB": 37.01171875,
  "controls": 192,
  "initial_controls": 72,
  "gradient_control": {
    "target_id": "AF-A0A2I1GTA6-F1-model_v6",
    "decoder_gradient_norm": 30.829551696777344,
    "gradient_parameters": 411,
    "prediction_max_abs": 0.0,
    "gradient_max_abs": 0.0,
    "losses": [
      1.790338397026062,
      1.790338397026062
    ],
    "token_gradient_norm": 0.029069550335407257,
    "pair_gradient_norm": 0.05989132076501846,
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
      "mean_motif_rmsd": 5.130291683639721,
      "mean_scaffold_rmsd": 0.39790604471164837
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.264728971980933,
      "mean_scaffold_rmsd": 0.39652956149885593
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.103790384692953,
      "mean_scaffold_rmsd": 0.5490719789992806
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 5.210331343389258,
      "mean_scaffold_rmsd": 0.5455686684007373
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
          "mean": 2.8786621437117024,
          "ci95": [
            2.4997032392557705,
            3.31050219615281
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
          "mean": -0.13443728834121246,
          "ci95": [
            -0.2630658223195148,
            -0.012637111396091952
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
          "mean": -0.10654095869630538,
          "ci95": [
            -0.2907613499684925,
            0.07871218713186653
          ],
          "families": 32
        }
      }
    }
  ],
  "scope": "Repeated training-only diagnostic. Full decoder adapted with coordinate flow matching. Native contexts are oracle controls. Latent arrays are masked decoder inputs, not predicted codes. Eligibility only excludes mathematically impossible improvement under unchanged joint/designability counts; actual same-refold results decide advancement."
}
```
