# Additional-family augmentation comparison

```json
{
  "status": "complete",
  "source_reports": [
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120060.json",
      "sha256": "f1d63f347fbd71bba5c5c897ba02a5bc4034fe66d33e694aa48f02ce229f4f1c"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120141.json",
      "sha256": "9096808439b304819f9e60cf7d36868b5df4d0512ca2c3332148d65f3350d7cf"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120178.json",
      "sha256": "6f3dbd096b6823895d130fdc98a01b38859a732483edb31583d40e7d4568abdf"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/extra_fragment_refold_50120232.json",
      "sha256": "aa3bbe70788207c41c05234ea446bce810c50c82ac0f82a7368873a214928ea5"
    }
  ],
  "summaries": [
    {
      "arm": "control512",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 23,
      "primary_successes": 9,
      "scaffold_successes": 9,
      "successful_families": 4,
      "successes_with_passing_native_control": 8
    },
    {
      "arm": "null512",
      "cohort": "all",
      "samples": 256,
      "raw_matches": 1,
      "primary_successes": 0,
      "scaffold_successes": 0,
      "successful_families": 0,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "control512",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 13,
      "primary_successes": 8,
      "scaffold_successes": 8,
      "successful_families": 3,
      "successes_with_passing_native_control": 8
    },
    {
      "arm": "null512",
      "cohort": "short",
      "samples": 128,
      "raw_matches": 1,
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
      "primary_successes": 1,
      "scaffold_successes": 1,
      "successful_families": 1,
      "successes_with_passing_native_control": 0
    },
    {
      "arm": "null512",
      "cohort": "long",
      "samples": 128,
      "raw_matches": 0,
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
        "mean": 0.0859375,
        "ci95": [
          0.0390625,
          0.140625
        ],
        "families": 64
      },
      "strict_joint_success": {
        "mean": 0.03515625,
        "ci95": [
          0.00390625,
          0.078125
        ],
        "families": 64
      },
      "scaffold_joint_success": {
        "mean": 0.03515625,
        "ci95": [
          0.00390625,
          0.078125
        ],
        "families": 64
      },
      "baseline_arm": "null512",
      "candidate_arm": "control512"
    },
    {
      "training_proteins": 512,
      "cohort": "short",
      "raw_gate_passed": {
        "mean": 0.09375,
        "ci95": [
          0.0234375,
          0.1796875
        ],
        "families": 32
      },
      "strict_joint_success": {
        "mean": 0.0625,
        "ci95": [
          0.0,
          0.1484375
        ],
        "families": 32
      },
      "scaffold_joint_success": {
        "mean": 0.0625,
        "ci95": [
          0.0,
          0.1484375
        ],
        "families": 32
      },
      "baseline_arm": "null512",
      "candidate_arm": "control512"
    },
    {
      "training_proteins": 512,
      "cohort": "long",
      "raw_gate_passed": {
        "mean": 0.078125,
        "ci95": [
          0.0234375,
          0.1484375
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
      "baseline_arm": "null512",
      "candidate_arm": "control512"
    }
  ],
  "completed_refolds": 704,
  "scope": "Additional development families; not a locked test. Same-refold scaffold success is the endpoint. All256outputs/model retained, with raw failures counted unsuccessful; their unconstrained designability is unmeasured. Bootstrap intervals describe family variation, not training-seed replication. Corpus-size comparisons have different parent histories and update counts. No evaluation labels enter training."
}
```
