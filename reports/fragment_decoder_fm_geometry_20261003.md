# Decoder-conditioning geometry diagnosis

```json
{
  "status": "complete",
  "profile_only": false,
  "manifest_sha256": "5f1a29cd95d73039f4adc385bc4024f21b5937bdf0404c01c16a75af265b3ad8",
  "source_report_sha256": "53038c0a4e44b36ab6cc80448a44cae635e367664b21300a32c182bcc0800de9",
  "summary": [
    {
      "arm": "parent",
      "samples": 128,
      "boundary_ca_gaps": 0,
      "boundary_peptide_outliers": 0,
      "clash_failure": 0,
      "clashes_scaffold_only": 4,
      "clashes_touching_motif": 0,
      "gap_failure": 0,
      "motif_ca_gaps": 0,
      "motif_fit_without_geometry": 25,
      "motif_peptide_outliers": 1,
      "peptide_failure": 0,
      "scaffold_ca_gaps": 0,
      "scaffold_peptide_outliers": 72
    },
    {
      "arm": "native_direct",
      "samples": 128,
      "boundary_ca_gaps": 0,
      "boundary_peptide_outliers": 1,
      "clash_failure": 0,
      "clashes_scaffold_only": 0,
      "clashes_touching_motif": 0,
      "gap_failure": 0,
      "motif_ca_gaps": 0,
      "motif_fit_without_geometry": 128,
      "motif_peptide_outliers": 4,
      "peptide_failure": 0,
      "scaffold_ca_gaps": 0,
      "scaffold_peptide_outliers": 136
    },
    {
      "arm": "generated_cond",
      "samples": 128,
      "boundary_ca_gaps": 198,
      "boundary_peptide_outliers": 253,
      "clash_failure": 106,
      "clashes_scaffold_only": 8,
      "clashes_touching_motif": 906,
      "gap_failure": 60,
      "motif_ca_gaps": 65,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 1753,
      "peptide_failure": 128,
      "scaffold_ca_gaps": 35,
      "scaffold_peptide_outliers": 4805
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "boundary_ca_gaps": 193,
      "boundary_peptide_outliers": 254,
      "clash_failure": 112,
      "clashes_scaffold_only": 8,
      "clashes_touching_motif": 1034,
      "gap_failure": 56,
      "motif_ca_gaps": 63,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 1766,
      "peptide_failure": 128,
      "scaffold_ca_gaps": 35,
      "scaffold_peptide_outliers": 4746
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "boundary_ca_gaps": 209,
      "boundary_peptide_outliers": 253,
      "clash_failure": 106,
      "clashes_scaffold_only": 4,
      "clashes_touching_motif": 893,
      "gap_failure": 72,
      "motif_ca_gaps": 76,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 1804,
      "peptide_failure": 128,
      "scaffold_ca_gaps": 69,
      "scaffold_peptide_outliers": 5680
    },
    {
      "arm": "native_null",
      "samples": 128,
      "boundary_ca_gaps": 194,
      "boundary_peptide_outliers": 253,
      "clash_failure": 110,
      "clashes_scaffold_only": 4,
      "clashes_touching_motif": 964,
      "gap_failure": 77,
      "motif_ca_gaps": 117,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 1827,
      "peptide_failure": 128,
      "scaffold_ca_gaps": 70,
      "scaffold_peptide_outliers": 5598
    }
  ],
  "transitions": {
    "retained_raw": 0,
    "lost_raw": 25,
    "new_raw": 0
  },
  "scope": "Post hoc description of every output, with unchanged eligibility and no checkpoint selection. Regions refer to supplied20residue motif and its complement; all decoded atoms are free. Latent arrays are masked INPUTS, so no latent reconstruction accuracy is claimed. Bond/clash/gap categories overlap. Learning windows draw different proteins, not paired validation. Geometry cannot establish designability; only the same-valid-refold assay can."
}
```
