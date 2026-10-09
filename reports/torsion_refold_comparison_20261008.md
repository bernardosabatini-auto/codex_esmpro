# Torsion-closure designability comparison

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
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50392677.json",
      "sha256": "d01979e19cc02a61deaaa3bd8c2db086e42094f7322332764f404002969fbd54"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50392728.json",
      "sha256": "dc7e8b37fe850e8f3627b6c2adf799fb88e84108aa23ff084eaba8dcde87026b"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50392771.json",
      "sha256": "40528826705dda5204e9a0fd17e7c912e0c9f1892d3b82493cf75f518f3355a0"
    },
    {
      "path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/reports/fragment_preference_refold_50392833.json",
      "sha256": "48377b4d80fa611501234053d24f397d511a190fb56802531a105a03cb6791d9"
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
      "arm": "torsion_closure",
      "bucket": null,
      "samples": 128,
      "complete_strict": 8,
      "valid_designable": 20,
      "connected_designable": 16,
      "complete_connected_designable": 14,
      "strict_families": 6
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
      "arm": "torsion_closure",
      "bucket": 128,
      "samples": 32,
      "complete_strict": 3,
      "valid_designable": 8,
      "connected_designable": 6,
      "complete_connected_designable": 6,
      "strict_families": 2
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
      "arm": "torsion_closure",
      "bucket": 256,
      "samples": 32,
      "complete_strict": 4,
      "valid_designable": 8,
      "connected_designable": 7,
      "complete_connected_designable": 6,
      "strict_families": 3
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
      "arm": "torsion_closure",
      "bucket": 384,
      "samples": 32,
      "complete_strict": 1,
      "valid_designable": 4,
      "connected_designable": 3,
      "complete_connected_designable": 2,
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
      "arm": "torsion_closure",
      "bucket": 512,
      "samples": 32,
      "complete_strict": 0,
      "valid_designable": 0,
      "connected_designable": 0,
      "complete_connected_designable": 0,
      "strict_families": 0
    }
  ],
  "contrasts": [
    {
      "bucket": null,
      "metrics": {
        "complete_strict": {
          "mean": 0.0,
          "ci95": [
            -0.0390625,
            0.046875
          ],
          "families": 32
        },
        "valid_designable": {
          "mean": -0.1953125,
          "ci95": [
            -0.28125,
            -0.1171875
          ],
          "families": 32
        },
        "connected_designable": {
          "mean": -0.2109375,
          "ci95": [
            -0.3125,
            -0.1171875
          ],
          "families": 32
        },
        "complete_connected_designable": {
          "mean": -0.2265625,
          "ci95": [
            -0.328125,
            -0.1328125
          ],
          "families": 32
        }
      }
    },
    {
      "bucket": 128,
      "metrics": {
        "complete_strict": {
          "mean": 0.0,
          "ci95": [
            -0.125,
            0.15625
          ],
          "families": 8
        },
        "valid_designable": {
          "mean": -0.28125,
          "ci95": [
            -0.40625,
            -0.15625
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.3125,
          "ci95": [
            -0.53125,
            -0.125
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.3125,
          "ci95": [
            -0.53125,
            -0.125
          ],
          "families": 8
        }
      }
    },
    {
      "bucket": 256,
      "metrics": {
        "complete_strict": {
          "mean": 0.0,
          "ci95": [
            -0.09375,
            0.09375
          ],
          "families": 8
        },
        "valid_designable": {
          "mean": -0.375,
          "ci95": [
            -0.59375,
            -0.1875
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.375,
          "ci95": [
            -0.625,
            -0.15625
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.40625,
          "ci95": [
            -0.65625,
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
          "mean": -0.0625,
          "ci95": [
            -0.15625,
            0.0
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.09375,
          "ci95": [
            -0.1875,
            -0.03125
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.125,
          "ci95": [
            -0.25,
            -0.03125
          ],
          "families": 8
        }
      }
    },
    {
      "bucket": 512,
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
          "mean": -0.0625,
          "ci95": [
            -0.15625,
            0.0
          ],
          "families": 8
        },
        "connected_designable": {
          "mean": -0.0625,
          "ci95": [
            -0.15625,
            0.0
          ],
          "families": 8
        },
        "complete_connected_designable": {
          "mean": -0.0625,
          "ci95": [
            -0.15625,
            0.0
          ],
          "families": 8
        }
      }
    }
  ],
  "gate": {
    "strict": false,
    "families": false,
    "designability": false
  },
  "qualified": false,
  "completed_new_refolds": 1024,
  "reused_parent_refolds": 1024,
  "diagnostics": [
    {
      "subset": "all",
      "samples": 128,
      "candidate_atom_overlap_cases": 73,
      "parent_atom_overlap_cases": 1,
      "median_phi_psi_change_degrees": 45.51875909161268
    },
    {
      "subset": "physical",
      "samples": 61,
      "candidate_atom_overlap_cases": 18,
      "parent_atom_overlap_cases": 0,
      "median_phi_psi_change_degrees": 28.49447416683458
    },
    {
      "subset": "designable",
      "samples": 20,
      "candidate_atom_overlap_cases": 2,
      "parent_atom_overlap_cases": 0,
      "median_phi_psi_change_degrees": 21.559841835114206
    },
    {
      "subset": "not_designable",
      "samples": 108,
      "candidate_atom_overlap_cases": 71,
      "parent_atom_overlap_cases": 1,
      "median_phi_psi_change_degrees": 48.135387631649465
    }
  ],
  "scope": "All128cases/arm; four distinct historical parent partitions, matched8attempt budgets. SAME-refold motif/global/scaffold/edge success, raw physical gate explicit. Posthoc atom-overlap/torsion diagnostics are descriptive, not new gates. Training-only; no learned-model or generalization claim."
}
```
