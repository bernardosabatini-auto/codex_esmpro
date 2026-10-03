# Additional-family augmentation comparison

```json
{
  "status": "complete",
  "source_reports": [
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50130616.json",
      "sha256": "abd847b56096e226b043e6b3a8b01a5f7bf88b62b50c77f8a48fb46b2f6d7fd5"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50130707.json",
      "sha256": "5260181448c94fcb120aaf2d13d944c1244d48189de8f362a0340821458f84ca"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50130778.json",
      "sha256": "6dd44ba75fef7a226afa4b016541703ece5dd30ae0caddc2413481c39077c4fb"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50130833.json",
      "sha256": "130407021f7112cb781313fd428997b885eee9e20814a4149d83fad069462272"
    }
  ],
  "summaries": [
    {
      "arm": "control_weight3",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 22,
      "primary_successes": 6,
      "scaffold_successes": 6,
      "successful_families": 3,
      "successes_with_passing_native_control": 5
    },
    {
      "arm": "control_balanced",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 17,
      "primary_successes": 4,
      "scaffold_successes": 4,
      "successful_families": 3,
      "successes_with_passing_native_control": 4
    },
    {
      "arm": "broad_weight3",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 50,
      "primary_successes": 8,
      "scaffold_successes": 6,
      "successful_families": 5,
      "successes_with_passing_native_control": 4
    },
    {
      "arm": "broad_balanced",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 45,
      "primary_successes": 10,
      "scaffold_successes": 5,
      "successful_families": 5,
      "successes_with_passing_native_control": 2
    },
    {
      "arm": "control_weight3",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 14,
      "primary_successes": 5,
      "scaffold_successes": 5,
      "successful_families": 2,
      "successes_with_passing_native_control": 5
    },
    {
      "arm": "control_balanced",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 9,
      "primary_successes": 4,
      "scaffold_successes": 4,
      "successful_families": 3,
      "successes_with_passing_native_control": 4
    },
    {
      "arm": "broad_weight3",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 31,
      "primary_successes": 8,
      "scaffold_successes": 6,
      "successful_families": 5,
      "successes_with_passing_native_control": 4
    },
    {
      "arm": "broad_balanced",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 31,
      "primary_successes": 9,
      "scaffold_successes": 4,
      "successful_families": 4,
      "successes_with_passing_native_control": 2
    },
    {
      "arm": "control_weight3",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 8,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control_balanced",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 8,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "broad_weight3",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 19,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "broad_balanced",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 14,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 0
    }
  ],
  "paired_family_contrasts": [
    {
      "training_proteins": 512,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": -0.01953125,
        "ci95": [
          -0.05078125,
          0.0078125
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.02734375,
          0.0078125
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.02734375,
          0.0078125
        ],
        "families": 64
      },
      "baseline_arm": "control_weight3",
      "candidate_arm": "control_balanced"
    },
    {
      "training_proteins": 7941,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": -0.01953125,
        "ci95": [
          -0.0546875,
          0.01171875
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          -0.01171875,
          0.02734375
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": -0.00390625,
        "ci95": [
          -0.01953125,
          0.01171875
        ],
        "families": 64
      },
      "baseline_arm": "broad_weight3",
      "candidate_arm": "broad_balanced"
    },
    {
      "training_proteins": 7941,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": 0.109375,
        "ci95": [
          0.05859375,
          0.1640625
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          -0.01171875,
          0.03125
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
          0.01953125
        ],
        "families": 64
      },
      "baseline_arm": "control_weight3",
      "candidate_arm": "broad_weight3"
    },
    {
      "training_proteins": 7941,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": 0.109375,
        "ci95": [
          0.05078125,
          0.171875
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.0234375,
        "ci95": [
          0.00390625,
          0.046875
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": 0.00390625,
        "ci95": [
          -0.015625,
          0.0234375
        ],
        "families": 64
      },
      "baseline_arm": "control_balanced",
      "candidate_arm": "broad_balanced"
    },
    {
      "training_proteins": 512,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": -0.0390625,
        "ci95": [
          -0.09375,
          0.015625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.046875,
          0.0234375
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.046875,
          0.0234375
        ],
        "families": 32
      },
      "baseline_arm": "control_weight3",
      "candidate_arm": "control_balanced"
    },
    {
      "training_proteins": 7941,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": 0.0,
        "ci95": [
          -0.0390625,
          0.0390625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          -0.0234375,
          0.0390625
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": -0.015625,
        "ci95": [
          -0.046875,
          0.015625
        ],
        "families": 32
      },
      "baseline_arm": "broad_weight3",
      "candidate_arm": "broad_balanced"
    },
    {
      "training_proteins": 7941,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": 0.1328125,
        "ci95": [
          0.0546875,
          0.2109375
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0234375,
        "ci95": [
          -0.015625,
          0.0625
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          -0.0390625,
          0.046875
        ],
        "families": 32
      },
      "baseline_arm": "control_weight3",
      "candidate_arm": "broad_weight3"
    },
    {
      "training_proteins": 7941,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": 0.171875,
        "ci95": [
          0.078125,
          0.265625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0390625,
        "ci95": [
          0.0078125,
          0.078125
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.0390625,
          0.0390625
        ],
        "families": 32
      },
      "baseline_arm": "control_balanced",
      "candidate_arm": "broad_balanced"
    },
    {
      "training_proteins": 512,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
          0.0234375
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.0234375,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.0234375,
          0.0
        ],
        "families": 32
      },
      "baseline_arm": "control_weight3",
      "candidate_arm": "control_balanced"
    },
    {
      "training_proteins": 7941,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": -0.0390625,
        "ci95": [
          -0.0859375,
          0.0078125
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          0.0,
          0.0234375
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          0.0,
          0.0234375
        ],
        "families": 32
      },
      "baseline_arm": "broad_weight3",
      "candidate_arm": "broad_balanced"
    },
    {
      "training_proteins": 7941,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": 0.0859375,
        "ci95": [
          0.015625,
          0.1640625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.0234375,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.0234375,
          0.0
        ],
        "families": 32
      },
      "baseline_arm": "control_weight3",
      "candidate_arm": "broad_weight3"
    },
    {
      "training_proteins": 7941,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": 0.046875,
        "ci95": [
          -0.015625,
          0.1171875
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          0.0,
          0.0234375
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          0.0,
          0.0234375
        ],
        "families": 32
      },
      "baseline_arm": "control_balanced",
      "candidate_arm": "broad_balanced"
    }
  ],
  "completed_refolds": 1944,
  "scope": "Additional development comparison of matched8000-update endpoints; not a locked test. Every256output denominator retained. Strict success requires the SAME valid refold. Secondary designability uses a fixed32-family slot0 panel independent of raw success. Original native budgets reused without pooling. Family bootstrap is not training-seed replication. No evaluation labels enter training.",
  "fixed_panel_designability": {
    "target_ids": [
      "1wv3_A",
      "3rnv_A",
      "6aoz_B",
      "6gf6_A",
      "6gh8_D",
      "7bb3_A",
      "7clu_A",
      "7tgh_3C",
      "8acc_A",
      "8b6h_DW",
      "8b6h_EB",
      "8cen_h",
      "8f2n_A",
      "8har_A",
      "8iuf_4G",
      "8iuf_6B",
      "8iuf_QB",
      "8kde_3",
      "8p0j_H",
      "8t5j_A",
      "8xqx_G",
      "9b40_A",
      "9c1g_0",
      "9d93_Sa",
      "9dtr_D",
      "9fq8_4I",
      "9fq8_4J",
      "9fq8_4R",
      "9fzl_3K",
      "9g6k_LY",
      "9h4p_QG",
      "9i05_XC"
    ],
    "summaries": [
      {
        "arm": "control_weight3",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 14
      },
      {
        "arm": "control_balanced",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 15
      },
      {
        "arm": "broad_weight3",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 5
      },
      {
        "arm": "broad_balanced",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 8
      },
      {
        "arm": "control_weight3",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 9
      },
      {
        "arm": "control_balanced",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 10
      },
      {
        "arm": "broad_weight3",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 4
      },
      {
        "arm": "broad_balanced",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 4
      },
      {
        "arm": "control_weight3",
        "cohort": "long",
        "samples": 16,
        "valid_designable": 5
      },
      {
        "arm": "control_balanced",
        "cohort": "long",
        "samples": 16,
        "valid_designable": 5
      },
      {
        "arm": "broad_weight3",
        "cohort": "long",
        "samples": 16,
        "valid_designable": 1
      },
      {
        "arm": "broad_balanced",
        "cohort": "long",
        "samples": 16,
        "valid_designable": 4
      }
    ],
    "paired_family_contrasts": [
      {
        "cohort": "all",
        "baseline_arm": "control_weight3",
        "candidate_arm": "control_balanced",
        "candidate_minus_baseline": {
          "mean": 0.03125,
          "ci95": [
            0.0,
            0.09375
          ],
          "families": 32
        }
      },
      {
        "cohort": "all",
        "baseline_arm": "broad_weight3",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": 0.09375,
          "ci95": [
            0.0,
            0.18828124999998863
          ],
          "families": 32
        }
      },
      {
        "cohort": "all",
        "baseline_arm": "control_weight3",
        "candidate_arm": "broad_weight3",
        "candidate_minus_baseline": {
          "mean": -0.28125,
          "ci95": [
            -0.4375,
            -0.125
          ],
          "families": 32
        }
      },
      {
        "cohort": "all",
        "baseline_arm": "control_balanced",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": -0.21875,
          "ci95": [
            -0.375,
            -0.0625
          ],
          "families": 32
        }
      },
      {
        "cohort": "short",
        "baseline_arm": "control_weight3",
        "candidate_arm": "control_balanced",
        "candidate_minus_baseline": {
          "mean": 0.0625,
          "ci95": [
            0.0,
            0.1875
          ],
          "families": 16
        }
      },
      {
        "cohort": "short",
        "baseline_arm": "broad_weight3",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 16
        }
      },
      {
        "cohort": "short",
        "baseline_arm": "control_weight3",
        "candidate_arm": "broad_weight3",
        "candidate_minus_baseline": {
          "mean": -0.3125,
          "ci95": [
            -0.5625,
            -0.125
          ],
          "families": 16
        }
      },
      {
        "cohort": "short",
        "baseline_arm": "control_balanced",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": -0.375,
          "ci95": [
            -0.625,
            -0.125
          ],
          "families": 16
        }
      },
      {
        "cohort": "long",
        "baseline_arm": "control_weight3",
        "candidate_arm": "control_balanced",
        "candidate_minus_baseline": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 16
        }
      },
      {
        "cohort": "long",
        "baseline_arm": "broad_weight3",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": 0.1875,
          "ci95": [
            0.0,
            0.375
          ],
          "families": 16
        }
      },
      {
        "cohort": "long",
        "baseline_arm": "control_weight3",
        "candidate_arm": "broad_weight3",
        "candidate_minus_baseline": {
          "mean": -0.25,
          "ci95": [
            -0.4375,
            -0.0625
          ],
          "families": 16
        }
      },
      {
        "cohort": "long",
        "baseline_arm": "control_balanced",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": -0.0625,
          "ci95": [
            -0.25,
            0.125
          ],
          "families": 16
        }
      }
    ]
  },
  "reused_native_sources": [
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120060/manifest.json",
      "manifest_sha256": "d518fc97c83ba401d12125209374365bfe6228b805522211db69c4966a50b5f7",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120060.json",
      "report_sha256": "f1d63f347fbd71bba5c5c897ba02a5bc4034fe66d33e694aa48f02ce229f4f1c",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120060/refolded.h5",
      "refolded_sha256": "756e8fd2fd0b2624c08038f3d4bf6f0d0dae6ee4eae8d24d7126b75aaf6d2118",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_short_refold_0.h5",
      "predictions_sha256": "30809a95fcbeae6924995fa2957fc3ae0cd28e749d97a98324df3765f0c31aaa"
    },
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120141/manifest.json",
      "manifest_sha256": "6e116e529f1dd6a7130591b86722fbbda7f0063e059999d08a7d629437552fac",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120141.json",
      "report_sha256": "9096808439b304819f9e60cf7d36868b5df4d0512ca2c3332148d65f3350d7cf",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120141/refolded.h5",
      "refolded_sha256": "86d1c8c47a82816ce08dbcc9a0151d20ba89285fe3d549cf3d2ce0958e323b1c",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_short_refold_1.h5",
      "predictions_sha256": "ef6b66418d3eac97bb59056f82750a75a5d0e5d6025153c44e6e99c370116c49"
    },
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120178/manifest.json",
      "manifest_sha256": "d5b901ca58b7dcaa1fbd47e8ac43720b31224bf4c3a80c49ca86d5f3e0ac9599",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120178.json",
      "report_sha256": "6f3dbd096b6823895d130fdc98a01b38859a732483edb31583d40e7d4568abdf",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120178/refolded.h5",
      "refolded_sha256": "5097bccdf3d3da91f6396d6d87f451132953e5e1be62c918d6e6a8dcec283423",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_short_refold_2.h5",
      "predictions_sha256": "0b11a02f2163684e7f10102563f03917e62c7b3d4a3dcbad4e8d42d46fd3ed4f"
    },
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120232/manifest.json",
      "manifest_sha256": "a1ba0de55b8731e94fce70ffdc1f76d0fe51a6a007fd103c4e75ede081417b1c",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120232.json",
      "report_sha256": "aa3bbe70788207c41c05234ea446bce810c50c82ac0f82a7368873a214928ea5",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50120232/refolded.h5",
      "refolded_sha256": "e5644955cebbfe3a606a0364deb2e92cf9ef6f3577891de3e65f316556ded509",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_short_refold_3.h5",
      "predictions_sha256": "aae965831b5487bc3675f197c354905c1e9dfa97c76b9e1a8208324ada8f5dc7"
    }
  ]
}
```
