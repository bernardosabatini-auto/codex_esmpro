# Fixed motif sequence compatibility: CPU diagnostic

Descriptive four-family diagnostic. Neither likelihood nor geometry qualifies training positives or proves designability. Do not launch GPU guidance from this result alone without a distinct prospectively defined objective and matched same-valid-refold assay. No reopening the closed strength/time-window recipe.

```json
{
  "summary": [
    {
      "arm": "native",
      "stage": "raw",
      "n": 4,
      "mean_motif_nll": 2.2927405834198,
      "mean_reverse_minus_actual": 1.3791248202323914,
      "mean_ca_aligned_allatom_rmsd": 2.2209459030439159e-07
    },
    {
      "arm": "native",
      "stage": "refold",
      "n": 3,
      "mean_motif_nll": 1.9612858295440674,
      "mean_reverse_minus_actual": 2.1007553736368814,
      "mean_ca_aligned_allatom_rmsd": 1.2559309404816033
    },
    {
      "arm": "baseline",
      "stage": "raw",
      "n": 16,
      "mean_motif_nll": 3.1417879313230515,
      "mean_reverse_minus_actual": 0.3557220548391342,
      "mean_ca_aligned_allatom_rmsd": 2.1619395031459536
    },
    {
      "arm": "baseline",
      "stage": "refold",
      "n": 4,
      "mean_motif_nll": 2.904272139072418,
      "mean_reverse_minus_actual": 0.5899056792259216,
      "mean_ca_aligned_allatom_rmsd": 3.4721782824721643
    },
    {
      "arm": "guided",
      "stage": "raw",
      "n": 16,
      "mean_motif_nll": 3.172664538025856,
      "mean_reverse_minus_actual": 0.22585177421569824,
      "mean_ca_aligned_allatom_rmsd": 0.7259842868253075
    },
    {
      "arm": "guided",
      "stage": "refold",
      "n": 4,
      "mean_motif_nll": 2.8177878856658936,
      "mean_reverse_minus_actual": 0.9172274470329285,
      "mean_ca_aligned_allatom_rmsd": 4.107447811604319
    }
  ],
  "gradient_qualified": true,
  "controls": [
    {
      "target_id": "AF-A0A2I1GTA6-F1-model_v6",
      "pose_max_logprob_error": 3.695487976074219e-05,
      "gradient_finite": true,
      "finite_differences": [
        {
          "epsilon": 0.01,
          "analytic": 0.4984081983566284,
          "numeric": 0.4986405372619629,
          "passed": true
        },
        {
          "epsilon": 0.001,
          "analytic": 0.4984081983566284,
          "numeric": 0.4972219169139862,
          "passed": true
        },
        {
          "epsilon": 0.0001,
          "analytic": 0.4984081983566284,
          "numeric": 0.5006790161132812,
          "passed": true
        }
      ],
      "qualified": true
    },
    {
      "target_id": "AF-A0A673FGJ2-F1-model_v6",
      "pose_max_logprob_error": 3.0279159545898438e-05,
      "gradient_finite": true,
      "finite_differences": [
        {
          "epsilon": 0.01,
          "analytic": 0.5881963968276978,
          "numeric": 0.5882978439331055,
          "passed": true
        },
        {
          "epsilon": 0.001,
          "analytic": 0.5881963968276978,
          "numeric": 0.590205192565918,
          "passed": true
        },
        {
          "epsilon": 0.0001,
          "analytic": 0.5881963968276978,
          "numeric": 0.6055831909179688,
          "passed": true
        }
      ],
      "qualified": true
    },
    {
      "target_id": "AF-A0AAE1HAL9-F1-model_v6",
      "pose_max_logprob_error": 1.4781951904296875e-05,
      "gradient_finite": true,
      "finite_differences": [
        {
          "epsilon": 0.01,
          "analytic": 0.20618323981761932,
          "numeric": 0.20617246627807617,
          "passed": true
        },
        {
          "epsilon": 0.001,
          "analytic": 0.20618323981761932,
          "numeric": 0.20563600957393646,
          "passed": true
        },
        {
          "epsilon": 0.0001,
          "analytic": 0.20618323981761932,
          "numeric": 0.20503997802734375,
          "passed": true
        }
      ],
      "qualified": true
    },
    {
      "target_id": "AF-A0A6C0DXI0-F1-model_v6",
      "pose_max_logprob_error": 2.9087066650390625e-05,
      "gradient_finite": true,
      "finite_differences": [
        {
          "epsilon": 0.01,
          "analytic": 0.6914332509040833,
          "numeric": 0.6923437118530273,
          "passed": true
        },
        {
          "epsilon": 0.001,
          "analytic": 0.6914332509040833,
          "numeric": 0.6904601454734802,
          "passed": true
        },
        {
          "epsilon": 0.0001,
          "analytic": 0.6914332509040833,
          "numeric": 0.6997585296630859,
          "passed": true
        }
      ],
      "qualified": true
    }
  ]
}
```
