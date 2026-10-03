# Additional-family augmentation comparison

```json
{
  "status": "complete",
  "source_reports": [
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114647.json",
      "sha256": "e9c0be29baede6baf348cfac0c5a5bbe98e41a899a57c31b0d7844169e2aac7c"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114694.json",
      "sha256": "2f15e99df5c0cb59d978425e31551a0c28339c11b33aaa728aeca7687b163694"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114767.json",
      "sha256": "c3ed6cbc05683254af9d26d8756acea82b0fb6921ec8e6075c4392b7ed406a76"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50114824.json",
      "sha256": "d1838596606fb2ed15244ecaf0fc61602d876edf4dbbb1a43027e1c41675e477"
    }
  ],
  "summaries": [
    {
      "arm": "control128",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 23,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 1
    },
    {
      "arm": "augmented128",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 19,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control512",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 24,
      "primary_successes": 2,
      "scaffold_successes": 2,
      "successful_families": 2,
      "successes_with_passing_native_control": 2
    },
    {
      "arm": "augmented512",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 22,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control128",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 9,
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 1
    },
    {
      "arm": "augmented128",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 6,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control512",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 14,
      "primary_successes": 2,
      "scaffold_successes": 2,
      "successful_families": 2,
      "successes_with_passing_native_control": 2
    },
    {
      "arm": "augmented512",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 11,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control128",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 14,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "augmented128",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 13,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control512",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 10,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "augmented512",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 11,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    }
  ],
  "paired_family_contrasts": [
    {
      "training_proteins": 128,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": -0.015625,
        "ci95": [
          -0.04296875,
          0.0078125
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": -0.00390625,
        "ci95": [
          -0.01171875,
          0.0
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
      }
    },
    {
      "training_proteins": 512,
      "cohort": "all",
      "raw_gate_passed": {
        "mean": -0.0078125,
        "ci95": [
          -0.03125,
          0.01953125
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.01953125,
          0.0
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": -0.0078125,
        "ci95": [
          -0.01953125,
          0.0
        ],
        "families": 64
      }
    },
    {
      "training_proteins": 128,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": -0.0234375,
        "ci95": [
          -0.0703125,
          0.0078125
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
      }
    },
    {
      "training_proteins": 512,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": -0.0234375,
        "ci95": [
          -0.0546875,
          0.0078125
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": -0.015625,
        "ci95": [
          -0.0390625,
          0.0
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": -0.015625,
        "ci95": [
          -0.0390625,
          0.0
        ],
        "families": 32
      }
    },
    {
      "training_proteins": 128,
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
      }
    },
    {
      "training_proteins": 512,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": 0.0078125,
        "ci95": [
          -0.0234375,
          0.046875
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
      }
    }
  ],
  "completed_refolds": 1216,
  "scope": "Additional development families; not a locked test. Same-refold scaffold success is the endpoint. All256outputs/model retained, with raw failures counted unsuccessful; their unconstrained designability is unmeasured. Bootstrap intervals describe family variation, not training-seed replication. Corpus-size comparisons have different parent histories and update counts. No evaluation labels enter training."
}
```
