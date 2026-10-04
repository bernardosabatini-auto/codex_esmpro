# Wider-mask failure localization

```json
{
  "status": "complete",
  "source_report_sha256": "cc82d3e43458d14807c29005973bdb291700ad354b1e8dfe9089092535d15292",
  "predictions_sha256": "b2af425e0143e03793ad16ed3811ff2396c34d1febd5c36b7f925f66fd72fd6e",
  "summary": [
    {
      "arm": "generated_cond",
      "samples": 128,
      "hidden_edges": 2304,
      "far_edges": 27876,
      "hidden_bad_peptide": 1927,
      "far_bad_peptide": 3677,
      "hidden_ca_gaps": 380,
      "far_ca_gaps": 22,
      "peptide_failure": 128,
      "clash_failure": 112,
      "gap_failure": 86,
      "mean_hidden_ca_bond": 3.0829418133944273,
      "mean_hidden_peptide_bond": 2.771106941625476
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "hidden_edges": 2304,
      "far_edges": 27876,
      "hidden_bad_peptide": 1953,
      "far_bad_peptide": 4783,
      "hidden_ca_gaps": 375,
      "far_ca_gaps": 63,
      "peptide_failure": 128,
      "clash_failure": 100,
      "gap_failure": 81,
      "mean_hidden_ca_bond": 3.121648121625185,
      "mean_hidden_peptide_bond": 2.8060784842818975
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "hidden_edges": 2304,
      "far_edges": 27876,
      "hidden_bad_peptide": 2289,
      "far_bad_peptide": 1684,
      "hidden_ca_gaps": 2033,
      "far_ca_gaps": 40,
      "peptide_failure": 117,
      "clash_failure": 127,
      "gap_failure": 128,
      "mean_hidden_ca_bond": 11.313906233757734,
      "mean_hidden_peptide_bond": 11.789458453655243
    },
    {
      "arm": "native_untrained",
      "samples": 128,
      "hidden_edges": 2304,
      "far_edges": 27876,
      "hidden_bad_peptide": 2292,
      "far_bad_peptide": 1725,
      "hidden_ca_gaps": 2034,
      "far_ca_gaps": 106,
      "peptide_failure": 118,
      "clash_failure": 122,
      "gap_failure": 128,
      "mean_hidden_ca_bond": 11.7887589558959,
      "mean_hidden_peptide_bond": 12.162171021103859
    }
  ],
  "scope": "Exploratory failure localization after the fixed endpoint. Hidden edges touch the eight flanking residues; far excludes the fixed motif interior. No changed gate or extension."
}
```
