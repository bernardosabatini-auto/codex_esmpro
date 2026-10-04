# Frozen decoder integration diagnostic

```json
{
  "status": "complete",
  "manifest_sha256": "ee2f4579d6a5f7eab69f24842ade50d8ee639db45aed84834a74a8766a82a2a1",
  "predictions_sha256": "0fe3682a32d8033d62aff60cae0b0537dcb55cdedc1b9a58040e0402f0b5acd2",
  "source_manifest_sha256": "5f1a29cd95d73039f4adc385bc4024f21b5937bdf0404c01c16a75af265b3ad8",
  "protocol_sha256": "ecabbc9d02bbe63ef66961b23e0e0c25f13752974b630a41b0fd1ce5d0a50336",
  "controls": 100,
  "free_summary": [
    {
      "arm": "cond",
      "steps": 3,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 5.103790384692953,
      "peptide_failure": 128,
      "clash_failure": 106,
      "gap_failure": 72
    },
    {
      "arm": "cond",
      "steps": 10,
      "samples": 128,
      "raw": 0,
      "valid": 4,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 5.428866599239202,
      "peptide_failure": 110,
      "clash_failure": 104,
      "gap_failure": 86
    },
    {
      "arm": "null",
      "steps": 3,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 5.210331343389258,
      "peptide_failure": 128,
      "clash_failure": 110,
      "gap_failure": 77
    },
    {
      "arm": "null",
      "steps": 10,
      "samples": 128,
      "raw": 0,
      "valid": 2,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 5.598671993883675,
      "peptide_failure": 107,
      "clash_failure": 110,
      "gap_failure": 99
    }
  ],
  "path_summary": [
    {
      "arm": "cond",
      "t": 0.0,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 6.384308034416309,
      "peptide_failure": 128,
      "clash_failure": 119,
      "gap_failure": 128,
      "motif_coordinate_mse_nm2": 0.35131916555110365,
      "scaffold_coordinate_mse_nm2": 0.008510676572768716,
      "motif_fm": 0.35131564758842065,
      "scaffold_fm": 0.008510591350425258
    },
    {
      "arm": "cond",
      "t": 0.3333333333333333,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 3.790515485618494,
      "peptide_failure": 128,
      "clash_failure": 83,
      "gap_failure": 101,
      "motif_coordinate_mse_nm2": 0.0871598425146658,
      "scaffold_coordinate_mse_nm2": 0.0025506887841402204,
      "motif_fm": 0.19610526096705277,
      "scaffold_fm": 0.0057389214485488145
    },
    {
      "arm": "cond",
      "t": 0.6666666666666666,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 2.249667942235215,
      "peptide_failure": 128,
      "clash_failure": 26,
      "gap_failure": 50,
      "motif_coordinate_mse_nm2": 0.022040232441213448,
      "scaffold_coordinate_mse_nm2": 0.0010035171130766685,
      "motif_fm": 0.19834426768626245,
      "scaffold_fm": 0.009030842457524717
    },
    {
      "arm": "cond",
      "t": 0.9,
      "samples": 128,
      "raw": 20,
      "valid": 43,
      "motif_fit_without_geometry": 58,
      "mean_motif_rmsd": 1.0168293232156373,
      "peptide_failure": 85,
      "clash_failure": 0,
      "gap_failure": 18,
      "motif_coordinate_mse_nm2": 0.0035814954917441355,
      "scaffold_coordinate_mse_nm2": 0.00014974284698610063,
      "motif_fm": 0.3577916236873045,
      "scaffold_fm": 0.014959319781978968
    },
    {
      "arm": "null",
      "t": 0.0,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 6.1919232403065285,
      "peptide_failure": 128,
      "clash_failure": 116,
      "gap_failure": 128,
      "motif_coordinate_mse_nm2": 0.27521436993265525,
      "scaffold_coordinate_mse_nm2": 0.008487809362122789,
      "motif_fm": 0.2752116140514561,
      "scaffold_fm": 0.008487724368761981
    },
    {
      "arm": "null",
      "t": 0.3333333333333333,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 4.152010581645959,
      "peptide_failure": 128,
      "clash_failure": 93,
      "gap_failure": 104,
      "motif_coordinate_mse_nm2": 0.0916721301182406,
      "scaffold_coordinate_mse_nm2": 0.0025810951274252147,
      "motif_fm": 0.20625768107851108,
      "scaffold_fm": 0.005807334191308811
    },
    {
      "arm": "null",
      "t": 0.6666666666666666,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 0,
      "mean_motif_rmsd": 2.42062503927728,
      "peptide_failure": 128,
      "clash_failure": 30,
      "gap_failure": 53,
      "motif_coordinate_mse_nm2": 0.02445386740146205,
      "scaffold_coordinate_mse_nm2": 0.0010029023274000792,
      "motif_fm": 0.22006503038372305,
      "scaffold_fm": 0.009025309883622316
    },
    {
      "arm": "null",
      "t": 0.9,
      "samples": 128,
      "raw": 12,
      "valid": 40,
      "motif_fit_without_geometry": 36,
      "mean_motif_rmsd": 1.0660011841813133,
      "peptide_failure": 88,
      "clash_failure": 0,
      "gap_failure": 22,
      "motif_coordinate_mse_nm2": 0.0038982213409326505,
      "scaffold_coordinate_mse_nm2": 0.00014913079564848886,
      "motif_fm": 0.38943255583593417,
      "scaffold_fm": 0.014898175815060987
    },
    {
      "arm": "original_unmasked",
      "t": 0.0,
      "samples": 128,
      "raw": 0,
      "valid": 0,
      "motif_fit_without_geometry": 128,
      "mean_motif_rmsd": 0.31634287726447463,
      "peptide_failure": 128,
      "clash_failure": 0,
      "gap_failure": 85,
      "motif_coordinate_mse_nm2": 0.0006502166311292967,
      "scaffold_coordinate_mse_nm2": 0.001640761528051371,
      "motif_fm": 0.000650210120132834,
      "scaffold_fm": 0.0016407450981540202
    },
    {
      "arm": "original_unmasked",
      "t": 0.3333333333333333,
      "samples": 128,
      "raw": 115,
      "valid": 115,
      "motif_fit_without_geometry": 128,
      "mean_motif_rmsd": 0.08937286249557846,
      "peptide_failure": 13,
      "clash_failure": 0,
      "gap_failure": 1,
      "motif_coordinate_mse_nm2": 6.486474423184063e-05,
      "scaffold_coordinate_mse_nm2": 0.000175483094508877,
      "motif_fm": 0.00014594241141504903,
      "scaffold_fm": 0.00039482813473623287
    },
    {
      "arm": "original_unmasked",
      "t": 0.6666666666666666,
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "motif_fit_without_geometry": 128,
      "mean_motif_rmsd": 0.058832965215183976,
      "peptide_failure": 0,
      "clash_failure": 0,
      "gap_failure": 0,
      "motif_coordinate_mse_nm2": 3.469881214357429e-05,
      "scaffold_coordinate_mse_nm2": 7.312598948061577e-05,
      "motif_fm": 0.000312261247813842,
      "scaffold_fm": 0.000658074767180973
    },
    {
      "arm": "original_unmasked",
      "t": 0.9,
      "samples": 128,
      "raw": 128,
      "valid": 128,
      "motif_fit_without_geometry": 128,
      "mean_motif_rmsd": 0.04126695404003358,
      "peptide_failure": 0,
      "clash_failure": 0,
      "gap_failure": 0,
      "motif_coordinate_mse_nm2": 1.7452231695358478e-05,
      "scaffold_coordinate_mse_nm2": 2.8754198947211762e-05,
      "motif_fm": 0.0017434790381959926,
      "scaffold_fm": 0.002872546273718906
    }
  ],
  "original_summary": {
    "arm": "original_native",
    "samples": 128,
    "raw": 128,
    "valid": 128,
    "motif_fit_without_geometry": 128,
    "mean_motif_rmsd": 0.07409355252235986,
    "peptide_failure": 0,
    "clash_failure": 0,
    "gap_failure": 0
  },
  "contrasts": [
    {
      "candidate": "cond_10",
      "reference": "cond_3",
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
          "mean": 0.03125,
          "ci95": [
            0.0078125,
            0.0625
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 0.32507621454624896,
          "ci95": [
            0.23370685543532688,
            0.4203258220893279
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "null_10",
      "reference": "null_3",
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
          "mean": 0.015625,
          "ci95": [
            0.0,
            0.046875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": 0.3883406504944171,
          "ci95": [
            0.2887402529778965,
            0.48857699384022824
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "cond_10",
      "reference": "null_10",
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
          "mean": 0.015625,
          "ci95": [
            -0.015625,
            0.046875
          ],
          "families": 32
        },
        "motif_ca_rmsd": {
          "mean": -0.16980539464447342,
          "ci95": [
            -0.3397878264944511,
            0.009625606511095144
          ],
          "families": 32
        }
      }
    },
    {
      "candidate": "cond_3",
      "reference": "null_3",
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
          "mean": -0.10654095869630532,
          "ci95": [
            -0.2852365257123108,
            0.08151404964695724
          ],
          "families": 32
        }
      }
    }
  ],
  "timing": [
    {
      "arm": "cond",
      "steps": 3,
      "seconds": 2.439342542551458
    },
    {
      "arm": "cond",
      "steps": 10,
      "seconds": 7.694594270549715
    },
    {
      "arm": "null",
      "steps": 3,
      "seconds": 2.311599710956216
    },
    {
      "arm": "null",
      "steps": 10,
      "seconds": 7.6948276734910905
    }
  ],
  "peak_reserved_GiB": 5.681640625,
  "elapsed_seconds": 70.97350998641923,
  "scope": "Frozen-model diagnostic on repeated32training proteins. All contexts are native oracles; t>0 path probes additionally contain native coordinates. Free sampling and oracle denoising are reported separately. No training, designability, refolding or generalization claim. Original3step failure is retained;10steps does not retrospectively qualify that recipe."
}
```
