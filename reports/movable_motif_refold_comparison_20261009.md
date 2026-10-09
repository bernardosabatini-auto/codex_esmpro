# Movable-motif designability comparison

```json
{
  "status": "complete",
  "source_reports": [
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50189270.json",
      "sha256": "c04c52d5c9b04b0916a28497088afac81bfb94153ae6415317359e667ee5c71b"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50189356.json",
      "sha256": "b8c8a69c614cce4683cedc7d2f64fa87500ccba70c36c182529dddfa9e15e8bc"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50189500.json",
      "sha256": "9cbcb24688c77d2896c5adcd13a077739f60d3baab283831ea49d4518bb70cf5"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50189577.json",
      "sha256": "7077f41f1389d87e9f46ee58eb393f9cda0d69f55acbd00fc3be0201ee21c365"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_51458371.json",
      "sha256": "647c96c4918a2e60cb42a123e469052ba4d7c4301c9944ebdcafbece1baacfee"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_51458615.json",
      "sha256": "23a2a36c79d9a4b84218eb448f28121c9a21e36ecb6bdaa43df9d64c941f3bdf"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_51458918.json",
      "sha256": "6e90b6752cbb9c9655192057690139cce76baf2ce39b8f3605d0dc6d432a7ec5"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_51459103.json",
      "sha256": "76a1dc65edc4c50c077aabc7edf5b520934009f02a64dcbbfe2758f5deedbc9f"
    }
  ],
  "baseline_comparison_sha256": "c3b5fbd78072e7bf528fd04ccc94931aea722e33e4617865d532476b0c439b41",
  "summary": [
    {
      "arm": "parent6000",
      "bucket": null,
      "samples": 128,
      "complete_strict": 8,
      "valid_designable": 45,
      "connected_designable": 43,
      "complete_connected_designable": 43,
      "strict_families": 7
    },
    {
      "arm": "movable_motif",
      "bucket": null,
      "samples": 128,
      "complete_strict": 12,
      "valid_designable": 25,
      "connected_designable": 24,
      "complete_connected_designable": 23,
      "strict_families": 9
    },
    {
      "arm": "parent6000",
      "bucket": 128,
      "samples": 32,
      "complete_strict": 3,
      "valid_designable": 17,
      "connected_designable": 16,
      "complete_connected_designable": 16,
      "strict_families": 2
    },
    {
      "arm": "movable_motif",
      "bucket": 128,
      "samples": 32,
      "complete_strict": 5,
      "valid_designable": 12,
      "connected_designable": 11,
      "complete_connected_designable": 11,
      "strict_families": 3
    },
    {
      "arm": "parent6000",
      "bucket": 256,
      "samples": 32,
      "complete_strict": 4,
      "valid_designable": 20,
      "connected_designable": 19,
      "complete_connected_designable": 19,
      "strict_families": 4
    },
    {
      "arm": "movable_motif",
      "bucket": 256,
      "samples": 32,
      "complete_strict": 5,
      "valid_designable": 8,
      "connected_designable": 8,
      "complete_connected_designable": 7,
      "strict_families": 4
    },
    {
      "arm": "parent6000",
      "bucket": 384,
      "samples": 32,
      "complete_strict": 1,
      "valid_designable": 6,
      "connected_designable": 6,
      "complete_connected_designable": 6,
      "strict_families": 1
    },
    {
      "arm": "movable_motif",
      "bucket": 384,
      "samples": 32,
      "complete_strict": 1,
      "valid_designable": 3,
      "connected_designable": 3,
      "complete_connected_designable": 3,
      "strict_families": 1
    },
    {
      "arm": "parent6000",
      "bucket": 512,
      "samples": 32,
      "complete_strict": 0,
      "valid_designable": 2,
      "connected_designable": 2,
      "complete_connected_designable": 2,
      "strict_families": 0
    },
    {
      "arm": "movable_motif",
      "bucket": 512,
      "samples": 32,
      "complete_strict": 1,
      "valid_designable": 2,
      "connected_designable": 2,
      "complete_connected_designable": 2,
      "strict_families": 1
    }
  ],
  "contrasts": [
    {
      "bucket": null,
      "metrics": {
        "complete_strict": {
          "mean": 0.03125,
          "ci95": [
            0.0,
            0.0703125
          ],
          "families": 32
        },
        "valid_designable": {
          "mean": -0.15625,
          "ci95": [
            -0.25,
            -0.0703125
          ],
          "families": 32
        },
        "connected_designable": {
          "mean": -0.1484375,
          "ci95": [
            -0.2421875,
            -0.0625
          ],
          "families": 32
        },
        "complete_connected_designable": {
          "mean": -0.15625,
          "ci95": [
            -0.25,
            -0.0703125
          ],
          "families": 32
        }
      }
    },
    {
      "bucket": 128,
      "metrics": {
        "complete_strict": {
          "mean": 0.0625,
          "ci95": [
            -0.0625,
            0.1875
          ],
          "families": 8
        },
        "valid_designable": {
          "mean": -0.15625,
          "ci95": [
            -0.28125,
            -0.03125
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.15625,
          "ci95": [
            -0.28125,
            -0.03125
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.15625,
          "ci95": [
            -0.28125,
            -0.03125
          ],
          "families": 8
        }
      }
    },
    {
      "bucket": 256,
      "metrics": {
        "complete_strict": {
          "mean": 0.03125,
          "ci95": [
            0.0,
            0.09375
          ],
          "families": 8
        },
        "valid_designable": {
          "mean": -0.375,
          "ci95": [
            -0.625,
            -0.125
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.34375,
          "ci95": [
            -0.59375,
            -0.09375
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.375,
          "ci95": [
            -0.59375,
            -0.1875
          ],
          "families": 8
        }
      }
    },
    {
      "bucket": 384,
      "metrics": {
        "complete_strict": {
          "mean": 0.0,
          "ci95": [
            0.0,
            0.0
          ],
          "families": 8
        },
        "valid_designable": {
          "mean": -0.09375,
          "ci95": [
            -0.25,
            0.0625
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.09375,
          "ci95": [
            -0.25,
            0.0625
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.09375,
          "ci95": [
            -0.25,
            0.0625
          ],
          "families": 8
        }
      }
    },
    {
      "bucket": 512,
      "metrics": {
        "complete_strict": {
          "mean": 0.03125,
          "ci95": [
            0.0,
            0.09375
          ],
          "families": 8
        },
        "valid_designable": {
          "mean": 0.0,
          "ci95": [
            -0.09375,
            0.09375
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": 0.0,
          "ci95": [
            -0.09375,
            0.09375
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": 0.0,
          "ci95": [
            -0.09375,
            0.09375
          ],
          "families": 8
        }
      }
    }
  ],
  "gate": {
    "strict": true,
    "families": true,
    "designability": false
  },
  "qualified": false,
  "completed_new_refolds": 1024,
  "reused_parent_refolds": 1024,
  "diagnostics": [
    {
      "subset": "all",
      "samples": 128,
      "candidate_atom_overlap_cases": 21,
      "parent_atom_overlap_cases": 1,
      "median_phi_psi_change_degrees": 22.410674235097297
    },
    {
      "subset": "physical",
      "samples": 77,
      "candidate_atom_overlap_cases": 0,
      "parent_atom_overlap_cases": 0,
      "median_phi_psi_change_degrees": 18.45416356778194
    },
    {
      "subset": "designable",
      "samples": 25,
      "candidate_atom_overlap_cases": 1,
      "parent_atom_overlap_cases": 0,
      "median_phi_psi_change_degrees": 12.85292244314122
    },
    {
      "subset": "not_designable",
      "samples": 103,
      "candidate_atom_overlap_cases": 20,
      "parent_atom_overlap_cases": 1,
      "median_phi_psi_change_degrees": 24.40651992645175
    }
  ],
  "scope": "Movable-motif construction, with shared raw nonbonded exclusion/threshold for parent and candidate. Advancement still requires exceeding the original historical8strict and45designable counts. All128cases/arm; four distinct historical parent partitions, matched8attempt budgets. SAME-refold motif/global/scaffold/edge success, raw physical gate explicit. Posthoc atom-overlap/torsion diagnostics are descriptive, not new gates. Training-only; no learned-model or generalization claim."
}
```
