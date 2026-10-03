# Whole-chain scaffold-clock flow

```json
{
  "status": "complete",
  "scaffold_clock": true,
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/scaffold_clock_training_50283116/manifest.json",
  "manifest_sha256": "3ad244d871e09a34c188fc91e39af74e2ca1c9d1a86593d6039f35e80085123e",
  "protocol_sha256": "64340c8708034fdee39c83cda42efcc32a9a47e99a13722a2417df21cc637036",
  "fragments_sha256": "31a03758906f5a33865f53c4176a7ce2420be4983c1ca7c2a38e8139b71103af",
  "checkpoint_sha256": "3be4284e887c6ada3f5e4d44fd5121446d5282bf5a19fe5a175810a6a0c91c58",
  "predictions_sha256": "d7ad0d56d1e2b5de2aa79f55974fd06af2bcbe5bb99c97ea3a653a3458d9378f",
  "updates": 2000,
  "trainable_parameters": 458738184,
  "training_seconds": 1169.7048059939407,
  "elapsed_seconds": 1503.177383616101,
  "peak_reserved_GiB": 29.15234375,
  "controls": 128,
  "saved_ema_gpu_replay": [
    {
      "arm": "generated_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0
    },
    {
      "arm": "native_cond",
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "latent_max_abs": 0.0
    }
  ],
  "initial_global_controls": 4,
  "prefix_max_abs": 1.8823891878128052e-05,
  "recommended_full_minutes": null,
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "raw": 25,
      "valid": 128,
      "mean_motif_rmsd": 2.251629539928018,
      "mean_scaffold_rmsd": 1.2388032569484769e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "mean_motif_rmsd": 0.07409355252235986,
      "mean_scaffold_rmsd": 1.1961144712089116e-14,
      "mean_scaffold_lddt": 1.0
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "raw": 23,
      "valid": 127,
      "mean_motif_rmsd": 2.565352320375946,
      "mean_scaffold_rmsd": 6.187082562698253,
      "mean_scaffold_lddt": 0.4864075148335529
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "raw": 3,
      "valid": 126,
      "mean_motif_rmsd": 5.636445558211449,
      "mean_scaffold_rmsd": 6.175045062439574,
      "mean_scaffold_lddt": 0.4866027995437634
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "raw": 46,
      "valid": 126,
      "mean_motif_rmsd": 1.912366082100125,
      "mean_scaffold_rmsd": 6.10316765694604,
      "mean_scaffold_lddt": 0.5577360226285899
    },
    {
      "arm": "native_null",
      "samples": 128,
      "raw": 13,
      "valid": 124,
      "mean_motif_rmsd": 4.824638923102674,
      "mean_scaffold_rmsd": 6.327496262051652,
      "mean_scaffold_lddt": 0.5415969429714831
    },
    {
      "arm": "initial_generated_cond",
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "mean_motif_rmsd": 2.4156144686099963,
      "mean_scaffold_rmsd": 6.448663203448447,
      "mean_scaffold_lddt": 0.4286448273020199
    }
  ],
  "refold_gate": {
    "qualified": false,
    "checks": {
      "native_capacity": false,
      "native_validity": true,
      "generated_validity": true,
      "raw_gain_over_parent": false,
      "raw_gain_over_null": true,
      "raw_gain_over_initial": true,
      "families": true
    },
    "improved_families": 4
  },
  "contrasts": [
    {
      "candidate": "generated_cond",
      "reference": "parent",
      "metrics": {
        "raw_gate_passed": {
          "mean": -0.015625,
          "ci95": [
            -0.0625,
            0.03125
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -0.0078125,
          "ci95": [
            -0.0234375,
            0.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 0.3137227804479278,
          "ci95": [
            0.036517403657286555,
            0.647986507092666
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
          "mean": 0.15625,
          "ci95": [
            0.078125,
            0.2421875
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.0078125,
          "ci95": [
            -0.015625,
            0.0390625
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -3.071093237835502,
          "ci95": [
            -3.5170461671736253,
            -2.644143227594807
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "generated_cond",
      "reference": "initial_generated_cond",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.1796875,
          "ci95": [
            0.09375,
            0.2734375
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.9921875,
          "ci95": [
            0.9765625,
            1.0
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 0.14973785176595011,
          "ci95": [
            -0.11200266843867356,
            0.4496036067851877
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
          "mean": 0.2578125,
          "ci95": [
            0.1484375,
            0.375
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": 0.015625,
          "ci95": [
            -0.015625,
            0.046875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -2.912272841002549,
          "ci95": [
            -3.3867241417172607,
            -2.414599500102318
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "native_cond",
      "reference": "generated_cond",
      "metrics": {
        "raw_gate_passed": {
          "mean": 0.1796875,
          "ci95": [
            0.09375,
            0.2734375
          ],
          "families": 32
        },
        "coarse_valid": {
          "mean": -0.0078125,
          "ci95": [
            -0.0390625,
            0.015625
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -0.6529862382758214,
          "ci95": [
            -0.8925403024022829,
            -0.4061202202017034
          ],
          "families": 32
        }
      }
    }
  ],
  "scope": "Repeated training-only capacity diagnostic. Whole scaffold is free to move. Raw capacity does not establish same-refold designability. Native-context outputs are oracle controls; no model promotion."
}
```
