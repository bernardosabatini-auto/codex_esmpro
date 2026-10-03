# Additional-family augmentation comparison

```json
{
  "status": "complete",
  "source_reports": [
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50130967.json",
      "sha256": "7fe921ee789e0986d30d1efad2f1b0d2dd373ec623496f22627d564bc9360e5c"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50131036.json",
      "sha256": "42953ec8377644e5c7d07dedc26dab8646ba7fdfc86107cbf2ea76d0c77971a0"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50131089.json",
      "sha256": "51693f00738b1ac93319a08b32afdc60bc19279596985b90da6f4b49b3e077d2"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50131153.json",
      "sha256": "a3b949da4a2f09049582b3e814d42156bc174fe1bce52057fd57d979ca6bd4ff"
    }
  ],
  "summaries": [
    {
      "arm": "control_weight3",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 30,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 1
    },
    {
      "arm": "control_balanced",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 28,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 1
    },
    {
      "arm": "broad_weight3",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 46,
      "primary_successes": 2,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "broad_balanced",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 43,
      "primary_successes": 2,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control_weight3",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 17,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 1
    },
    {
      "arm": "control_balanced",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 16,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 1
    },
    {
      "arm": "broad_weight3",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 27,
      "primary_successes": 2,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "broad_balanced",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 23,
      "primary_successes": 2,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control_weight3",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 13,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control_balanced",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 12,
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
      "raw_matches": 20,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    }
  ],
  "paired_family_contrasts": [
    {
      "training_proteins": 512,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": -0.0078125,
        "ci95": [
          -0.03515625,
          0.01953125
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.01171875,
          0.01171875
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.01171875,
          0.01171875
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
        "mean": -0.01171875,
        "ci95": [
          -0.03515625,
          0.01171875
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.01171875,
          0.01171875
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
        "mean": 0.0625,
        "ci95": [
          0.015625,
          0.11328125
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.00390625,
        "ci95": [
          -0.01171875,
          0.0234375
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": -0.00390625,
        "ci95": [
          -0.01171875,
          0.0
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
        "mean": 0.05859375,
        "ci95": [
          0.01171875,
          0.109375
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.00390625,
        "ci95": [
          -0.0078125,
          0.015625
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": -0.00390625,
        "ci95": [
          -0.01171875,
          0.0
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
        "mean": -0.0078125,
        "ci95": [
          -0.046875,
          0.03125
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
          0.0234375
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
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
        "mean": -0.03125,
        "ci95": [
          -0.0625,
          -0.0078125
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          -0.0234375,
          0.0234375
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
        "mean": 0.078125,
        "ci95": [
          0.0078125,
          0.15625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          -0.0234375,
          0.046875
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
      "cohort": "short",
      "raw_gate_passed": {
        "mean": 0.0546875,
        "ci95": [
          -0.0234375,
          0.140625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0078125,
        "ci95": [
          -0.015625,
          0.03125
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
      "baseline_arm": "control_balanced",
      "candidate_arm": "broad_balanced"
    },
    {
      "training_proteins": 512,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": -0.0078125,
        "ci95": [
          -0.0390625,
          0.0234375
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
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
        "mean": 0.0078125,
        "ci95": [
          -0.0234375,
          0.0390625
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
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
        "mean": 0.046875,
        "ci95": [
          -0.0078125,
          0.109375
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
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
        "mean": 0.0625,
        "ci95": [
          0.015625,
          0.125
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      },
      "baseline_arm": "control_balanced",
      "candidate_arm": "broad_balanced"
    }
  ],
  "completed_refolds": 2056,
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
        "valid_designable": 9
      },
      {
        "arm": "control_balanced",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 8
      },
      {
        "arm": "broad_weight3",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 3
      },
      {
        "arm": "broad_balanced",
        "cohort": "all",
        "samples": 32,
        "valid_designable": 4
      },
      {
        "arm": "control_weight3",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 7
      },
      {
        "arm": "control_balanced",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 7
      },
      {
        "arm": "broad_weight3",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 2
      },
      {
        "arm": "broad_balanced",
        "cohort": "short",
        "samples": 16,
        "valid_designable": 3
      },
      {
        "arm": "control_weight3",
        "cohort": "long",
        "samples": 16,
        "valid_designable": 2
      },
      {
        "arm": "control_balanced",
        "cohort": "long",
        "samples": 16,
        "valid_designable": 1
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
        "valid_designable": 1
      }
    ],
    "paired_family_contrasts": [
      {
        "cohort": "all",
        "baseline_arm": "control_weight3",
        "candidate_arm": "control_balanced",
        "candidate_minus_baseline": {
          "mean": -0.03125,
          "ci95": [
            -0.125,
            0.0625
          ],
          "families": 32
        }
      },
      {
        "cohort": "all",
        "baseline_arm": "broad_weight3",
        "candidate_arm": "broad_balanced",
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
        "baseline_arm": "control_weight3",
        "candidate_arm": "broad_weight3",
        "candidate_minus_baseline": {
          "mean": -0.1875,
          "ci95": [
            -0.34375,
            -0.03125
          ],
          "families": 32
        }
      },
      {
        "cohort": "all",
        "baseline_arm": "control_balanced",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": -0.125,
          "ci95": [
            -0.28125,
            0.0
          ],
          "families": 32
        }
      },
      {
        "cohort": "short",
        "baseline_arm": "control_weight3",
        "candidate_arm": "control_balanced",
        "candidate_minus_baseline": {
          "mean": 0.0,
          "ci95": [
            -0.1875,
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
        "baseline_arm": "control_weight3",
        "candidate_arm": "broad_weight3",
        "candidate_minus_baseline": {
          "mean": -0.3125,
          "ci95": [
            -0.5625,
            0.0
          ],
          "families": 16
        }
      },
      {
        "cohort": "short",
        "baseline_arm": "control_balanced",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": -0.25,
          "ci95": [
            -0.5,
            0.0
          ],
          "families": 16
        }
      },
      {
        "cohort": "long",
        "baseline_arm": "control_weight3",
        "candidate_arm": "control_balanced",
        "candidate_minus_baseline": {
          "mean": -0.0625,
          "ci95": [
            -0.1875,
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
        "baseline_arm": "control_weight3",
        "candidate_arm": "broad_weight3",
        "candidate_minus_baseline": {
          "mean": -0.0625,
          "ci95": [
            -0.1875,
            0.0
          ],
          "families": 16
        }
      },
      {
        "cohort": "long",
        "baseline_arm": "control_balanced",
        "candidate_arm": "broad_balanced",
        "candidate_minus_baseline": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 16
        }
      }
    ]
  },
  "reused_native_sources": [
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114647/manifest.json",
      "manifest_sha256": "74b49595c91f1a16c9e980bd9837178d9702a19bea328c92be2b64f6c7e1f708",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114647.json",
      "report_sha256": "e9c0be29baede6baf348cfac0c5a5bbe98e41a899a57c31b0d7844169e2aac7c",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114647/refolded.h5",
      "refolded_sha256": "aa3b0c74a589d4920a53a40ebc99f38d4df72ad97be296aa29be982e9fc43c46",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_0.h5",
      "predictions_sha256": "6c99c6f1bc48cdf81be0650088ac87ebfbd6243dc441472db4f40239333fe119"
    },
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114694/manifest.json",
      "manifest_sha256": "ccf72b3ca1a0a552b5fc1b3e9edc8b6261812d2cdd139ec915696de815cc87e3",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114694.json",
      "report_sha256": "2f15e99df5c0cb59d978425e31551a0c28339c11b33aaa728aeca7687b163694",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114694/refolded.h5",
      "refolded_sha256": "1f6bdc7c7556cad0fb9acb156da585818e7c93c91a372e729c751526c872fb96",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_1.h5",
      "predictions_sha256": "b578a819e561dfb33eef1daa4c3c6fa9dea4a38277535d2a837700734048f4ef"
    },
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114767/manifest.json",
      "manifest_sha256": "77d835b76632b65752aeb237b044de35b19eee8a356f957c5cc63a9ed05851d5",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114767.json",
      "report_sha256": "c3ed6cbc05683254af9d26d8756acea82b0fb6921ec8e6075c4392b7ed406a76",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114767/refolded.h5",
      "refolded_sha256": "136ad3d47ab4f86cbe3fba9ea711001bf36fdf77ffde3112065cd080c1052f79",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_2.h5",
      "predictions_sha256": "83bda84a8e0f88421fec355b5f37d2749f1dc0b960bc768437b54470d8e9b95f"
    },
    {
      "manifest": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114824/manifest.json",
      "manifest_sha256": "a182c51cf6d9e8e96c57b892905160314d1b30776d922d84c776a6d98b40ec0a",
      "report": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114824.json",
      "report_sha256": "d1838596606fb2ed15244ecaf0fc61602d876edf4dbbb1a43027e1c41675e477",
      "refolded": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_50114824/refolded.h5",
      "refolded_sha256": "f17ee64947295edf34d023ea4d50f3753d81f7ec3a95616d81e0f6419c663047",
      "predictions": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/extra_fragment_refold_3.h5",
      "predictions_sha256": "af4bb783c8abd1666858af2110e7b5c3f5abc87d73f6b09b9d4543ba10112bd0"
    }
  ]
}
```
