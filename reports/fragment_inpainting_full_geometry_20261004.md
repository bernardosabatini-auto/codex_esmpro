# Decoder-conditioning geometry diagnosis

```json
{
  "status": "complete",
  "profile_only": false,
  "manifest_sha256": "ce4ff9c7b685e76c5000dbe3116c721114551f394fe4d5c37c9bb9769e7f04a0",
  "source_report_sha256": "b6572611b192ab850bedff56523d12a0463e2f91892882b76ef79413e6994504",
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
      "boundary_ca_gaps": 169,
      "boundary_peptide_outliers": 246,
      "clash_failure": 18,
      "clashes_scaffold_only": 4,
      "clashes_touching_motif": 61,
      "gap_failure": 20,
      "motif_ca_gaps": 0,
      "motif_fit_without_geometry": 128,
      "motif_peptide_outliers": 0,
      "peptide_failure": 0,
      "scaffold_ca_gaps": 2,
      "scaffold_peptide_outliers": 182
    },
    {
      "arm": "generated_null",
      "samples": 128,
      "boundary_ca_gaps": 228,
      "boundary_peptide_outliers": 255,
      "clash_failure": 114,
      "clashes_scaffold_only": 3,
      "clashes_touching_motif": 865,
      "gap_failure": 93,
      "motif_ca_gaps": 309,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 2145,
      "peptide_failure": 111,
      "scaffold_ca_gaps": 8,
      "scaffold_peptide_outliers": 221
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "boundary_ca_gaps": 3,
      "boundary_peptide_outliers": 234,
      "clash_failure": 0,
      "clashes_scaffold_only": 0,
      "clashes_touching_motif": 0,
      "gap_failure": 0,
      "motif_ca_gaps": 0,
      "motif_fit_without_geometry": 128,
      "motif_peptide_outliers": 0,
      "peptide_failure": 6,
      "scaffold_ca_gaps": 2,
      "scaffold_peptide_outliers": 309
    },
    {
      "arm": "native_null",
      "samples": 128,
      "boundary_ca_gaps": 216,
      "boundary_peptide_outliers": 255,
      "clash_failure": 107,
      "clashes_scaffold_only": 0,
      "clashes_touching_motif": 818,
      "gap_failure": 103,
      "motif_ca_gaps": 408,
      "motif_fit_without_geometry": 0,
      "motif_peptide_outliers": 2215,
      "peptide_failure": 113,
      "scaffold_ca_gaps": 34,
      "scaffold_peptide_outliers": 408
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "boundary_ca_gaps": 177,
      "boundary_peptide_outliers": 255,
      "clash_failure": 21,
      "clashes_scaffold_only": 6,
      "clashes_touching_motif": 69,
      "gap_failure": 27,
      "motif_ca_gaps": 0,
      "motif_fit_without_geometry": 128,
      "motif_peptide_outliers": 0,
      "peptide_failure": 46,
      "scaffold_ca_gaps": 18,
      "scaffold_peptide_outliers": 765
    },
    {
      "arm": "native_untrained",
      "samples": 128,
      "boundary_ca_gaps": 190,
      "boundary_peptide_outliers": 246,
      "clash_failure": 6,
      "clashes_scaffold_only": 2,
      "clashes_touching_motif": 15,
      "gap_failure": 57,
      "motif_ca_gaps": 0,
      "motif_fit_without_geometry": 128,
      "motif_peptide_outliers": 0,
      "peptide_failure": 55,
      "scaffold_ca_gaps": 86,
      "scaffold_peptide_outliers": 948
    }
  ],
  "transitions": {
    "retained_raw": 24,
    "lost_raw": 1,
    "new_raw": 73
  },
  "scope": "Post hoc description of every output, with unchanged eligibility and no checkpoint selection. Regions refer to supplied20residue motif and its complement. Motif atoms are fixed in conditioned/untrained inpainting, and free in null controls. Latent arrays are masked INPUTS, so no latent reconstruction accuracy is claimed. Bond/clash/gap categories overlap. Learning windows draw different proteins, not paired validation. Geometry cannot establish designability; only the same-valid-refold assay can."
}
```

## Junction limitation

The coarse whole-chain score permits a small fraction of bad bonds. It therefore conceals disconnected supplied fragments. These outputs are not yet usable as intact generated chains, even if the fixed refolding assay later shows realizable motif/scaffold arrangements. No primary threshold or denominator is changed.

|Arm|Both junctions intact /128|Median boundary C–N (A)|
|---|---:|---:|
|parent|128|1.342|
|native_direct|127|1.352|
|generated_cond|0|4.317|
|generated_untrained|0|6.042|
|native_cond|2|2.068|
|native_untrained|0|6.110|

Both junctions must have C–N1.1–1.6A and CA separation<=4.5A. The fixed3-versus10-step diagnostic separates coarse integration from learned denoising failure before another training hypothesis is selected.
