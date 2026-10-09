# Fixed motif sequence compatibility: CPU diagnostic

Descriptive four-family diagnostic. Neither likelihood nor geometry qualifies training positives or proves designability. Do not launch GPU guidance from this result alone without a distinct prospectively defined objective and matched same-valid-refold assay. No reopening the closed strength/time-window recipe.

```json
{
  "summary": [
    {
      "arm": "native",
      "stage": "raw",
      "n": 4,
      "mean_motif_nll": 2.479180335998535,
      "mean_reverse_minus_actual": 1.1181656122207642,
      "mean_ca_aligned_allatom_rmsd": 2.2209459030439159e-07
    },
    {
      "arm": "native",
      "stage": "refold",
      "n": 3,
      "mean_motif_nll": 2.2078168392181396,
      "mean_reverse_minus_actual": 1.7833605607350667,
      "mean_ca_aligned_allatom_rmsd": 1.2559309404816033
    },
    {
      "arm": "baseline",
      "stage": "raw",
      "n": 16,
      "mean_motif_nll": 3.1713620722293854,
      "mean_reverse_minus_actual": 0.30065658688545227,
      "mean_ca_aligned_allatom_rmsd": 2.1619395031459536
    },
    {
      "arm": "baseline",
      "stage": "refold",
      "n": 4,
      "mean_motif_nll": 2.938460052013397,
      "mean_reverse_minus_actual": 0.6006798148155212,
      "mean_ca_aligned_allatom_rmsd": 3.4721782824721643
    },
    {
      "arm": "guided",
      "stage": "raw",
      "n": 16,
      "mean_motif_nll": 3.1552356630563736,
      "mean_reverse_minus_actual": 0.23300647735595703,
      "mean_ca_aligned_allatom_rmsd": 0.7259842868253075
    },
    {
      "arm": "guided",
      "stage": "refold",
      "n": 4,
      "mean_motif_nll": 2.7953826189041138,
      "mean_reverse_minus_actual": 0.9547849297523499,
      "mean_ca_aligned_allatom_rmsd": 4.107447811604319
    }
  ],
  "gradient_qualified": false,
  "controls": [
    {
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "pose_max_logprob_error": 0.019324421882629395,
      "gradient_finite": false,
      "nonfinite_elements": 330,
      "gradient_norm": null,
      "finite_differences": [],
      "qualified": false
    },
    {
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "pose_max_logprob_error": 0.025632858276367188,
      "gradient_finite": false,
      "nonfinite_elements": 711,
      "gradient_norm": null,
      "finite_differences": [],
      "qualified": false
    },
    {
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "pose_max_logprob_error": 0.026462316513061523,
      "gradient_finite": false,
      "nonfinite_elements": 777,
      "gradient_norm": null,
      "finite_differences": [],
      "qualified": false
    },
    {
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "pose_max_logprob_error": 0.0930790901184082,
      "gradient_finite": false,
      "nonfinite_elements": 1413,
      "gradient_norm": null,
      "finite_differences": [],
      "qualified": false
    }
  ]
}
```
