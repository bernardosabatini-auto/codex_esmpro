# Explicit isolated-fragment conditioning

Raw samples, without clamping, retry or filtering.32training families assess capacity;16experimental development families assess transfer. Geometry and motif retention alone do not establish designability. Family bootstrap intervals on this fixed panel are descriptive.

```json
{
  "status": "complete",
  "manifest_sha256": "700aaf3e3fa70fb6051138eb58b4b5c994a3f458c86468fa29351df17eac89f6",
  "updates": 2000,
  "total_training_updates": 8000,
  "audited_predictions": 1152,
  "training_seconds": 1169.5476439250633,
  "evaluation_seconds": 334.40913251880556,
  "elapsed_seconds": 1560.1100088651292,
  "max_reserved_GiB": 29.177734375,
  "profile_qualified": false,
  "capacity_gate_passed": true,
  "summaries": [
    {
      "step": 0,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 0.96875,
          "motif_fraction_under_1A": 0.3125,
          "joint_fraction": 0.296875,
          "mean_motif_drms": 1.4914270155131817,
          "mean_reference_ca_lddt": 0.332799251833676,
          "mean_pairwise_sample_ca_rmsd": 17.74305133119015
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.596949275583029,
          "mean_reference_ca_lddt": 0.2550187221901837,
          "mean_pairwise_sample_ca_rmsd": 18.558574568655914
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.296875,
        "ci95": [
          0.125,
          0.484375
        ],
        "families": 16
      }
    },
    {
      "step": 0,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.4375,
          "joint_fraction": 0.4296875,
          "mean_motif_drms": 2.850904241669923,
          "mean_reference_ca_lddt": 0.4094430875648414,
          "mean_pairwise_sample_ca_rmsd": 23.05949329501084
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.285800343379378,
          "mean_reference_ca_lddt": 0.2755835264187052,
          "mean_pairwise_sample_ca_rmsd": 24.33783364303818
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4296875,
        "ci95": [
          0.28125,
          0.578125
        ],
        "families": 32
      }
    },
    {
      "step": 500,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.328125,
          "joint_fraction": 0.328125,
          "mean_motif_drms": 1.4056473653763533,
          "mean_reference_ca_lddt": 0.34010907728965456,
          "mean_pairwise_sample_ca_rmsd": 16.82746186029568
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.31893440335989,
          "mean_reference_ca_lddt": 0.25631371651936474,
          "mean_pairwise_sample_ca_rmsd": 18.168798785001897
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.328125,
        "ci95": [
          0.140625,
          0.53125
        ],
        "families": 16
      }
    },
    {
      "step": 500,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.3984375,
          "joint_fraction": 0.3984375,
          "mean_motif_drms": 2.95277904253453,
          "mean_reference_ca_lddt": 0.4181472999792488,
          "mean_pairwise_sample_ca_rmsd": 23.025459840849045
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.9921875,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.195948164910078,
          "mean_reference_ca_lddt": 0.2805342300133118,
          "mean_pairwise_sample_ca_rmsd": 23.93459359429002
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.3984375,
        "ci95": [
          0.2578125,
          0.5390625
        ],
        "families": 32
      }
    },
    {
      "step": 2000,
      "cohort": "development",
      "arms": {
        "conditioned": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.390625,
          "joint_fraction": 0.390625,
          "mean_motif_drms": 1.300442824140191,
          "mean_reference_ca_lddt": 0.3447949619638947,
          "mean_pairwise_sample_ca_rmsd": 16.836533551720947
        },
        "null": {
          "samples": 64,
          "raw_valid_fraction": 1.0,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 7.450929060578346,
          "mean_reference_ca_lddt": 0.2607113808698173,
          "mean_pairwise_sample_ca_rmsd": 17.381468084757984
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.390625,
        "ci95": [
          0.203125,
          0.59375
        ],
        "families": 16
      }
    },
    {
      "step": 2000,
      "cohort": "train",
      "arms": {
        "conditioned": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.4453125,
          "joint_fraction": 0.4453125,
          "mean_motif_drms": 2.532776781124994,
          "mean_reference_ca_lddt": 0.42355761289204863,
          "mean_pairwise_sample_ca_rmsd": 23.336621246139373
        },
        "null": {
          "samples": 128,
          "raw_valid_fraction": 0.984375,
          "motif_fraction_under_1A": 0.0,
          "joint_fraction": 0.0,
          "mean_motif_drms": 13.289918333292007,
          "mean_reference_ca_lddt": 0.27427748539902075,
          "mean_pairwise_sample_ca_rmsd": 23.996292060828498
        }
      },
      "conditioned_minus_null_joint": {
        "mean": 0.4453125,
        "ci95": [
          0.3046875,
          0.59375
        ],
        "families": 32
      }
    }
  ],
  "initial_controls": 128,
  "sampling_controls": 4,
  "augmentation_contrast_audit": {
    "status": "complete",
    "matched_primary_steps": 2000,
    "identical_initial_samples": 384,
    "augmented_conditional_examples": 14405,
    "all_null_targets_unchanged": true,
    "baseline_manifest_sha256": "18e7e06531eac2d12020b0ac78703a2cbdddd2ad1f6d9c7b821f9e97c0a0cf16",
    "candidate_manifest_sha256": "700aaf3e3fa70fb6051138eb58b4b5c994a3f458c86468fa29351df17eac89f6"
  }
}
```
