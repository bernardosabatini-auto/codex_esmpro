# Decoder-conditioning geometry diagnosis

```json
{
  "status": "complete",
  "profile_only": false,
  "manifest_sha256": "2123692a610552840040aa5c0fab6c0474f21b692d88cfb66b763f6a12ba9f1e",
  "source_report_sha256": "c0ac2929ee0f078162a3433c2e9a9aa3bda7afb36054259f2af1b803cdf96c44",
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
      "boundary_ca_gaps": 223,
      "boundary_peptide_outliers": 254,
      "clash_failure": 123,
      "clashes_scaffold_only": 6,
      "clashes_touching_motif": 1609,
      "gap_failure": 128,
      "motif_ca_gaps": 790,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 2408,
      "peptide_failure": 120,
      "scaffold_ca_gaps": 12,
      "scaffold_peptide_outliers": 250
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "boundary_ca_gaps": 244,
      "boundary_peptide_outliers": 254,
      "clash_failure": 128,
      "clashes_scaffold_only": 9,
      "clashes_touching_motif": 1393,
      "gap_failure": 128,
      "motif_ca_gaps": 2080,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 2411,
      "peptide_failure": 122,
      "scaffold_ca_gaps": 28,
      "scaffold_peptide_outliers": 657
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "boundary_ca_gaps": 227,
      "boundary_peptide_outliers": 255,
      "clash_failure": 126,
      "clashes_scaffold_only": 6,
      "clashes_touching_motif": 1613,
      "gap_failure": 125,
      "motif_ca_gaps": 834,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 2415,
      "peptide_failure": 120,
      "scaffold_ca_gaps": 71,
      "scaffold_peptide_outliers": 378
    },
    {
      "arm": "native_null",
      "samples": 128,
      "boundary_ca_gaps": 249,
      "boundary_peptide_outliers": 256,
      "clash_failure": 127,
      "clashes_scaffold_only": 9,
      "clashes_touching_motif": 1339,
      "gap_failure": 128,
      "motif_ca_gaps": 2078,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 2413,
      "peptide_failure": 122,
      "scaffold_ca_gaps": 104,
      "scaffold_peptide_outliers": 779
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
