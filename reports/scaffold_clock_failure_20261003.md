# Whole-chain adjustment failure diagnosis

```json
{
  "status": "complete",
  "source_report_sha256": "bd6667ff0d9b687ac29cd520701ccc2209430bf26ac6abfd1ea120a29960835b",
  "manifest_sha256": "3ad244d871e09a34c188fc91e39af74e2ca1c9d1a86593d6039f35e80085123e",
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "motif_fit_without_geometry": 25,
      "peptide_failure": 0,
      "clash_failure": 0,
      "gap_failure": 0,
      "window_peptide_outliers": 1,
      "window_ca_gaps": 0,
      "boundary_peptide_outliers": 0,
      "boundary_ca_gaps": 0,
      "scaffold_peptide_outliers": 72,
      "scaffold_ca_gaps": 0,
      "clashes_touching_window": 1,
      "clashes_scaffold_only": 3
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "motif_fit_without_geometry": 128,
      "peptide_failure": 0,
      "clash_failure": 0,
      "gap_failure": 0,
      "window_peptide_outliers": 13,
      "window_ca_gaps": 0,
      "boundary_peptide_outliers": 1,
      "boundary_ca_gaps": 0,
      "scaffold_peptide_outliers": 127,
      "scaffold_ca_gaps": 0,
      "clashes_touching_window": 0,
      "clashes_scaffold_only": 0,
      "mean_window_latent_mse_to_native": 0.0
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "motif_fit_without_geometry": 23,
      "peptide_failure": 0,
      "clash_failure": 1,
      "gap_failure": 0,
      "window_peptide_outliers": 3,
      "window_ca_gaps": 0,
      "boundary_peptide_outliers": 1,
      "boundary_ca_gaps": 1,
      "scaffold_peptide_outliers": 59,
      "scaffold_ca_gaps": 2,
      "clashes_touching_window": 8,
      "clashes_scaffold_only": 8
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "motif_fit_without_geometry": 3,
      "peptide_failure": 0,
      "clash_failure": 2,
      "gap_failure": 0,
      "window_peptide_outliers": 3,
      "window_ca_gaps": 0,
      "boundary_peptide_outliers": 1,
      "boundary_ca_gaps": 1,
      "scaffold_peptide_outliers": 51,
      "scaffold_ca_gaps": 1,
      "clashes_touching_window": 7,
      "clashes_scaffold_only": 4
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "motif_fit_without_geometry": 48,
      "peptide_failure": 1,
      "clash_failure": 1,
      "gap_failure": 0,
      "window_peptide_outliers": 3,
      "window_ca_gaps": 0,
      "boundary_peptide_outliers": 3,
      "boundary_ca_gaps": 0,
      "scaffold_peptide_outliers": 167,
      "scaffold_ca_gaps": 8,
      "clashes_touching_window": 6,
      "clashes_scaffold_only": 6,
      "mean_window_latent_mse_to_native": 0.2209366377483093
    },
    {
      "arm": "native_null",
      "samples": 128,
      "motif_fit_without_geometry": 14,
      "peptide_failure": 1,
      "clash_failure": 3,
      "gap_failure": 0,
      "window_peptide_outliers": 1,
      "window_ca_gaps": 0,
      "boundary_peptide_outliers": 2,
      "boundary_ca_gaps": 0,
      "scaffold_peptide_outliers": 178,
      "scaffold_ca_gaps": 4,
      "clashes_touching_window": 9,
      "clashes_scaffold_only": 2,
      "mean_window_latent_mse_to_native": 0.28227072787922225
    }
  ],
  "scope": "Post hoc localization on the same 32 repeatedly used training proteins, four draws each. Window means supplied motif plus eight flanking residues; scaffold means the remaining residues. All regions were free to move. Bond/clash/gap categories overlap. Native context is an oracle, not generated success. Transition counts are not a promoted selection policy. No designability was measured for this failed arm; all refold gates remain unchanged.",
  "transitions": {
    "retained_raw": 9,
    "lost_raw": 16,
    "new_raw": 14
  },
  "native_endpoint_errors": [
    {
      "arm": "native_cond",
      "samples": 128,
      "mean_window_mse": 0.2209366377483093,
      "mean_scaffold_mse": 0.04870077119994676
    },
    {
      "arm": "native_null",
      "samples": 128,
      "mean_window_mse": 0.28227072787922225,
      "mean_scaffold_mse": 0.05218751628854079
    }
  ],
  "refold_export_rejects_failed_run": true,
  "protocol_sha256": "64340c8708034fdee39c83cda42efcc32a9a47e99a13722a2417df21cc637036"
}
```
