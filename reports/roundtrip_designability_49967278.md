# Reconstruction consistency versus measured designability

```json
{
  "status": "complete",
  "manifest_sha256": "c556679a7fe2ca21afb5f819442cb13b9109a121e1e4d98df0cfb73c772d2944",
  "roundtrips_sha256": "fd13a65e1e3a6a6f2332e34ce4ec0d89e762068404ba885869c810a03a530565",
  "reconstructions": 152,
  "native_controls": 12,
  "native_controls_under_1A": 12,
  "summaries": {
    "training": {
      "backbones": 16,
      "families": 8,
      "designable": 5,
      "pooled_auc": 0.38181818181818183,
      "family_bootstrap_ci95": [
        0.15860615079365079,
        0.6875
      ],
      "bootstrap_defined_draws": 1999,
      "mixed_label_families": 5,
      "within_family_auc": 0.4
    },
    "development": {
      "backbones": 48,
      "families": 4,
      "designable": 18,
      "pooled_auc": 0.6351851851851852,
      "family_bootstrap_ci95": [
        0.4627949183303085,
        0.7333333333333333
      ],
      "bootstrap_defined_draws": 2000,
      "mixed_label_families": 4,
      "within_family_auc": 0.5080357142857143
    }
  },
  "exploratory_followup_qualified": false,
  "interpretation": "Existing-label exploratory diagnostic. Native controls excluded; predictive analyses use generated coarse-valid backbones. A pass would require fresh training-family refold validation before proxy optimization. No motif success inferred.",
  "elapsed_seconds": 38.80247528292239,
  "measurement_seconds": 5.194578988943249,
  "peak_reserved_GiB": 1.095703125
}
```
