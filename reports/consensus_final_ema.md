# Reference-free three-sample selection

Choices frozen before opening native score files; no native coordinates used.

Exploratory diagnostic on 626 reused development proteins. Select the CA lDDT medoid of three predictions, with no native input and no fitted coefficients. This uses three generated samples per selected prediction.

| Metric | Baseline | Selected | Change [95% cluster CI] |
|---|---:|---:|---|
| tm_fixed_reference, first_sample | 0.56857 | 0.57367 | +0.00510 [0.002701460100791493, 0.007611824125984414] |
| tm_fixed_reference, sample_mean | 0.56824 | 0.57367 | +0.00543 [0.003580402607988014, 0.007337033623539502] |
| ca_lddt, first_sample | 0.67427 | 0.67836 | +0.00409 [0.002061119629335027, 0.0062181423031450415] |
| ca_lddt, sample_mean | 0.67450 | 0.67836 | +0.00386 [0.0024486137775302564, 0.005336048057499494] |

Eligible for independent inference-noise replication: True. No final-test targets scored.

Native-TM best-of-three is an oracle upper bound only: 0.5892019009584664. It is not the selected model accuracy.

```json
{
  "status": "complete",
  "selection_sha256": "118c6c24a825519957da36801aa2e3f39414c344b083376daf39eb08649ff54a",
  "scores_sha256": "6e6ac44594af9146ae0b2aa6fea6042407d68e99b434863ccc7c16a0a430de74",
  "clusters_sha256": "b4af3184ee7089bb6ebfdbd948442514c922add27807569f2a976b6999450e72",
  "pairs": {
    "tm_fixed_reference": {
      "first_sample": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5685665974440894,
        "theirs": 0.5736656549520767,
        "theirs_minus_ours": 0.0050990575079872215,
        "ci95": [
          0.002701460100791493,
          0.007611824125984414
        ],
        "ours_wins": 183,
        "ties": 209,
        "coverage": 1.0
      },
      "sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5682384930777423,
        "theirs": 0.5736656549520767,
        "theirs_minus_ours": 0.005427161874334396,
        "ci95": [
          0.003580402607988014,
          0.007337033623539502
        ],
        "ours_wins": 260,
        "ties": 0,
        "coverage": 1.0
      }
    },
    "ca_lddt": {
      "first_sample": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.674274316111646,
        "theirs": 0.6783631452277615,
        "theirs_minus_ours": 0.0040888291161156306,
        "ci95": [
          0.002061119629335027,
          0.0062181423031450415
        ],
        "ours_wins": 183,
        "ties": 211,
        "coverage": 1.0
      },
      "sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.6745045193931416,
        "theirs": 0.6783631452277615,
        "theirs_minus_ours": 0.0038586258346200333,
        "ci95": [
          0.0024486137775302564,
          0.005336048057499494
        ],
        "ours_wins": 268,
        "ties": 1,
        "coverage": 1.0
      }
    }
  },
  "geometry": {
    "predicted_ca_gaps_on_reference_short": {
      "selected_total": 247,
      "sample_mean_total": 272.00000000000006,
      "difference": -25.000000000000057
    },
    "peptide_length_outliers_on_reference_short": {
      "selected_total": 538,
      "sample_mean_total": 589.0000000000003,
      "difference": -51.00000000000034
    }
  },
  "oracle_tm_only": {
    "n": 626,
    "clusters": 606,
    "bootstrap_unit": "cluster",
    "ours": 0.5682384930777423,
    "theirs": 0.5892019009584664,
    "theirs_minus_ours": 0.020963407880724174,
    "ci95": [
      0.01928215353301435,
      0.022809015095058293
    ],
    "ours_wins": 0,
    "ties": 0,
    "coverage": 1.0
  },
  "eligible_for_noise_replication": true,
  "selection_seconds": 12.350726170931011,
  "diagnostic_only": true
}
```
