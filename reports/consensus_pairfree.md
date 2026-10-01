# Reference-free three-sample selection

Choices frozen before opening native score files; no native coordinates used.

Exploratory diagnostic on 626 reused development proteins. Select the CA lDDT medoid of three predictions, with no native input and no fitted coefficients. This uses three generated samples per selected prediction.

| Metric | Baseline | Selected | Change [95% cluster CI] |
|---|---:|---:|---|
| tm_fixed_reference, first_sample | 0.55772 | 0.56230 | +0.00458 [0.0017859018185799706, 0.007407728550609433] |
| tm_fixed_reference, sample_mean | 0.55934 | 0.56230 | +0.00296 [0.0010662526042473182, 0.004923732004253054] |
| ca_lddt, first_sample | 0.66624 | 0.67141 | +0.00517 [0.003256718000127474, 0.007207574176866473] |
| ca_lddt, sample_mean | 0.66709 | 0.67141 | +0.00432 [0.0028445371286108935, 0.005863982572454188] |

Eligible for independent inference-noise replication: True. No final-test targets scored.

Native-TM best-of-three is an oracle upper bound only: 0.5822957188498403. It is not the selected model accuracy.

```json
{
  "status": "complete",
  "selection_sha256": "05cdfcbc4408279d2220bb49ec54279db999d35a5ebe579efe49dfa8841ff525",
  "scores_sha256": "38d06bce5a35172adc296853c0501b8ffcdf18265ba55000c30870c2f752aef9",
  "clusters_sha256": "b4af3184ee7089bb6ebfdbd948442514c922add27807569f2a976b6999450e72",
  "pairs": {
    "tm_fixed_reference": {
      "first_sample": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5577246485623003,
        "theirs": 0.5622997923322683,
        "theirs_minus_ours": 0.004575143769968051,
        "ci95": [
          0.0017859018185799706,
          0.007407728550609433
        ],
        "ours_wins": 188,
        "ties": 210,
        "coverage": 1.0
      },
      "sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5593393982960597,
        "theirs": 0.5622997923322683,
        "theirs_minus_ours": 0.0029603940362087308,
        "ci95": [
          0.0010662526042473182,
          0.004923732004253054
        ],
        "ours_wins": 294,
        "ties": 0,
        "coverage": 1.0
      }
    },
    "ca_lddt": {
      "first_sample": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.6662373848106156,
        "theirs": 0.67141220993641,
        "theirs_minus_ours": 0.005174825125794451,
        "ci95": [
          0.003256718000127474,
          0.007207574176866473
        ],
        "ours_wins": 161,
        "ties": 211,
        "coverage": 1.0
      },
      "sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.6670933953998498,
        "theirs": 0.67141220993641,
        "theirs_minus_ours": 0.00431881453656015,
        "ci95": [
          0.0028445371286108935,
          0.005863982572454188
        ],
        "ours_wins": 249,
        "ties": 0,
        "coverage": 1.0
      }
    }
  },
  "geometry": {
    "predicted_ca_gaps_on_reference_short": {
      "selected_total": 217,
      "sample_mean_total": 224.99999999999986,
      "difference": -7.999999999999858
    },
    "peptide_length_outliers_on_reference_short": {
      "selected_total": 487,
      "sample_mean_total": 516.9999999999997,
      "difference": -29.99999999999966
    }
  },
  "oracle_tm_only": {
    "n": 626,
    "clusters": 606,
    "bootstrap_unit": "cluster",
    "ours": 0.5593393982960597,
    "theirs": 0.5822957188498403,
    "theirs_minus_ours": 0.022956320553780614,
    "ci95": [
      0.021118274305555552,
      0.024900396645110585
    ],
    "ours_wins": 0,
    "ties": 0,
    "coverage": 1.0
  },
  "eligible_for_noise_replication": true,
  "selection_seconds": 11.654169350047596,
  "diagnostic_only": true
}
```
