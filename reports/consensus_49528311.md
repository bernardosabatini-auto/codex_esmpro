# Three-sample consensus: independent inference noise

Same untouched checkpoint, frozen selection rule, all development targets. These vary inference noise, not training seeds or target population. The initial screen is excluded from the replication-only pooled comparison.

| Inference seed | Mean TM | Selected TM | Selection gain [95% cluster CI] |
|---:|---:|---:|---|
| 2026100101 | 0.56697 | 0.57049 | +0.00352 [0.0015915221944902416, 0.0054841022221268345] |
| 2026100102 | 0.56775 | 0.57142 | +0.00368 [0.0018537039780998446, 0.005518717018425115] |

No independent-test scoring or accuracy promotion follows from this diagnostic alone.

```json
{
  "status": "complete",
  "runs": {
    "consensus_49528311_0": {
      "seed": 2026100101,
      "status": "complete",
      "selection_sha256": "eb134c66215b87c3c886f005f0973ad16c61a536d6fa23d697d5f1088b2ce865",
      "scores_sha256": "4ade872d77f1c7e836ce471ff2b8dc98cd99558419d5c54e2074eb645118cb21",
      "clusters_sha256": "b4af3184ee7089bb6ebfdbd948442514c922add27807569f2a976b6999450e72",
      "pairs": {
        "tm_fixed_reference": {
          "first_sample": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.5682150319488819,
            "theirs": 0.5704908945686902,
            "theirs_minus_ours": 0.002275862619808306,
            "ci95": [
              -0.00039043327390087673,
              0.005120646984288546
            ],
            "ours_wins": 192,
            "ties": 203,
            "coverage": 1.0
          },
          "sample_mean": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.5669724760383386,
            "theirs": 0.5704908945686902,
            "theirs_minus_ours": 0.0035184185303514374,
            "ci95": [
              0.0015915221944902416,
              0.0054841022221268345
            ],
            "ours_wins": 270,
            "ties": 0,
            "coverage": 1.0
          }
        },
        "ca_lddt": {
          "first_sample": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.6741985983096329,
            "theirs": 0.675929469810995,
            "theirs_minus_ours": 0.0017308715013620985,
            "ci95": [
              -0.00023009774210110462,
              0.003726344473824364
            ],
            "ours_wins": 201,
            "ties": 203,
            "coverage": 1.0
          },
          "sample_mean": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.6724854549201918,
            "theirs": 0.675929469810995,
            "theirs_minus_ours": 0.0034440148908031136,
            "ci95": [
              0.0020336750915469497,
              0.004888215836658657
            ],
            "ours_wins": 269,
            "ties": 0,
            "coverage": 1.0
          }
        }
      },
      "geometry": {
        "predicted_ca_gaps_on_reference_short": {
          "selected_total": 258,
          "sample_mean_total": 282.6666666666666,
          "difference": -24.666666666666572
        },
        "peptide_length_outliers_on_reference_short": {
          "selected_total": 563,
          "sample_mean_total": 581.3333333333331,
          "difference": -18.333333333333144
        }
      },
      "oracle_tm_only": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5669724760383386,
        "theirs": 0.5892788338658147,
        "theirs_minus_ours": 0.022306357827476038,
        "ci95": [
          0.02039515551862458,
          0.024469969428420495
        ],
        "ours_wins": 0,
        "ties": 0,
        "coverage": 1.0
      },
      "eligible_for_noise_replication": true,
      "selection_seconds": 11.5672158600064,
      "diagnostic_only": true,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 76.11471817495791,
          "SM Issue [Throughput %]": 59.485937772101934,
          "Tensor Active [Throughput %]": 0.89197190456841,
          "DRAM Read Bandwidth [Throughput %]": 10.975227840018576,
          "DRAM Write Bandwidth [Throughput %]": 6.437452835664945
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.34383863851245,
          "SM Issue [Throughput %]": 75.53675806282172,
          "Tensor Active [Throughput %]": 1.1262317470322514,
          "DRAM Read Bandwidth [Throughput %]": 13.861056833701019,
          "DRAM Write Bandwidth [Throughput %]": 7.972034877613194
        },
        "capture_seconds": 689.070845547,
        "collection_seconds": 475.940078734,
        "counter_period_ns": 10000012.27084331,
        "validated_intervals": 33,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    "consensus_49528311_1": {
      "seed": 2026100102,
      "status": "complete",
      "selection_sha256": "52c2d208f64f7ca75267a27c7578aa6d6d359b60136127639953a6ac79cbbd2e",
      "scores_sha256": "76ce9d89394281c46f78bf9a23bcb02183e49a481dc241e814c22287c631a95b",
      "clusters_sha256": "b4af3184ee7089bb6ebfdbd948442514c922add27807569f2a976b6999450e72",
      "pairs": {
        "tm_fixed_reference": {
          "first_sample": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.5683080990415336,
            "theirs": 0.571422268370607,
            "theirs_minus_ours": 0.0031141693290734824,
            "ci95": [
              0.00019722442291690307,
              0.006009082209260881
            ],
            "ours_wins": 197,
            "ties": 196,
            "coverage": 1.0
          },
          "sample_mean": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.5677463152289669,
            "theirs": 0.571422268370607,
            "theirs_minus_ours": 0.0036759531416400443,
            "ci95": [
              0.0018537039780998446,
              0.005518717018425115
            ],
            "ours_wins": 285,
            "ties": 0,
            "coverage": 1.0
          }
        },
        "ca_lddt": {
          "first_sample": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.6726317213434433,
            "theirs": 0.6771854706158358,
            "theirs_minus_ours": 0.00455374927239249,
            "ci95": [
              0.0022187907631872968,
              0.007003599379827719
            ],
            "ours_wins": 181,
            "ties": 197,
            "coverage": 1.0
          },
          "sample_mean": {
            "n": 626,
            "clusters": 606,
            "bootstrap_unit": "cluster",
            "ours": 0.6730122796775019,
            "theirs": 0.6771854706158358,
            "theirs_minus_ours": 0.004173190938333828,
            "ci95": [
              0.002845334047821792,
              0.005581187241745723
            ],
            "ours_wins": 234,
            "ties": 3,
            "coverage": 1.0
          }
        }
      },
      "geometry": {
        "predicted_ca_gaps_on_reference_short": {
          "selected_total": 246,
          "sample_mean_total": 276.6666666666666,
          "difference": -30.666666666666572
        },
        "peptide_length_outliers_on_reference_short": {
          "selected_total": 580,
          "sample_mean_total": 595.9999999999999,
          "difference": -15.999999999999886
        }
      },
      "oracle_tm_only": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5677463152289669,
        "theirs": 0.5901488658146964,
        "theirs_minus_ours": 0.022402550585729503,
        "ci95": [
          0.020545957677868015,
          0.02438350714492495
        ],
        "ours_wins": 0,
        "ties": 0,
        "coverage": 1.0
      },
      "eligible_for_noise_replication": true,
      "selection_seconds": 10.078084102016874,
      "diagnostic_only": true,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 76.3584894707052,
          "SM Issue [Throughput %]": 59.71343773130343,
          "Tensor Active [Throughput %]": 0.8935024599799718,
          "DRAM Read Bandwidth [Throughput %]": 10.976111344934182,
          "DRAM Write Bandwidth [Throughput %]": 6.434799645878989
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.38517959679785,
          "SM Issue [Throughput %]": 75.61377258057756,
          "Tensor Active [Throughput %]": 1.1252357600905318,
          "DRAM Read Bandwidth [Throughput %]": 13.826312921748606,
          "DRAM Write Bandwidth [Throughput %]": 7.949306341422524
        },
        "capture_seconds": 689.020048138,
        "collection_seconds": 477.218214515,
        "counter_period_ns": 10000000.698644452,
        "validated_intervals": 33,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    }
  },
  "failures": [],
  "inference_noise_replications": true,
  "training_replications": false,
  "replications_only_paired": {
    "tm_fixed_reference": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.5673593956336528,
      "theirs": 0.5709565814696486,
      "theirs_minus_ours": 0.0035971858359957433,
      "ci95": [
        0.002188462406195584,
        0.005066966486088821
      ],
      "ours_wins": 259,
      "ties": 0,
      "coverage": 1.0
    },
    "ca_lddt": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.672748867298847,
      "theirs": 0.6765574702134154,
      "theirs_minus_ours": 0.0038086029145684716,
      "ci95": [
        0.002790968571059853,
        0.0049064576484434946
      ],
      "ours_wins": 239,
      "ties": 1,
      "coverage": 1.0
    }
  }
}
```
