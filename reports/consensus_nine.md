# Nine-sample consensus budget diagnostic

Nine-sample choices written before opening native score files. Runtime includes HDF5 reads and three-sample parity checks; not optimized deployment latency.

Exploratory reuse of three already examined noise groups and 626 development proteins. The three-sample reference is its expectation over the three groups; coordinates are never averaged. Nine-sample selection needs three times the head/decoder sample budget. ESMC can be reused.

| Metric | Reference | Reference mean | Selected nine | Change [95% cluster CI] |
|---|---|---:|---:|---|
| tm_fixed_reference | nine_sample_mean | 0.56765 | 0.57539 | +0.00774 [0.005545699631082537, 0.01003168743215708] |
| tm_fixed_reference | three_sample_medoid_expectation | 0.57186 | 0.57539 | +0.00353 [0.0016499038246517409, 0.005470450087874144] |
| ca_lddt | nine_sample_mean | 0.67333 | 0.67913 | +0.00579 [0.0043654161746979, 0.007244250980625758] |
| ca_lddt | three_sample_medoid_expectation | 0.67716 | 0.67913 | +0.00197 [0.0006990851751648191, 0.0032342271219219934] |

Eligible for a new nine-sample noise pool: False. Native-TM best-of-nine is an oracle upper bound only. No accuracy promotion or final-test scoring.

```json
{
  "status": "complete",
  "choices_sha256": "e67e8c6381d4557c477d21cbfaeb2ea9a8fed74fbe8b18841af9c0adbf16768b",
  "protocol_sha256": "d084c89acf0c48ba046782b1d45ea43b893aa759c1d4a92686998d19aaf1e50a",
  "pairs": {
    "tm_fixed_reference": {
      "nine_sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5676524281150159,
        "theirs": 0.5753888498402556,
        "theirs_minus_ours": 0.007736421725239621,
        "ci95": [
          0.005545699631082537,
          0.01003168743215708
        ],
        "ours_wins": 257,
        "ties": 0,
        "coverage": 1.0
      },
      "three_sample_medoid_expectation": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.5718596059637913,
        "theirs": 0.5753888498402556,
        "theirs_minus_ours": 0.0035292438764643265,
        "ci95": [
          0.0016499038246517409,
          0.005470450087874144
        ],
        "ours_wins": 296,
        "ties": 0,
        "coverage": 1.0
      }
    },
    "ca_lddt": {
      "nine_sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.6733340846636118,
        "theirs": 0.6791273569991408,
        "theirs_minus_ours": 0.005793272335529036,
        "ci95": [
          0.0043654161746979,
          0.007244250980625758
        ],
        "ours_wins": 206,
        "ties": 0,
        "coverage": 1.0
      },
      "three_sample_medoid_expectation": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.677159361884864,
        "theirs": 0.6791273569991408,
        "theirs_minus_ours": 0.001967995114276712,
        "ci95": [
          0.0006990851751648191,
          0.0032342271219219934
        ],
        "ours_wins": 262,
        "ties": 1,
        "coverage": 1.0
      }
    }
  },
  "geometry": {
    "predicted_ca_gaps_on_reference_short": {
      "nine_sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.0017961682620839976,
        "theirs": 0.0014188213607509925,
        "theirs_minus_ours": -0.0003773469013330051,
        "ci95": [
          -0.0006099446144362091,
          -0.00015523330530490604
        ],
        "ours_wins": 123,
        "ties": 459,
        "coverage": 1.0
      },
      "three_sample_medoid_expectation": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.001616328122037048,
        "theirs": 0.0014188213607509925,
        "theirs_minus_ours": -0.0001975067612860558,
        "ci95": [
          -0.0004062791789413783,
          9.367831511093013e-06
        ],
        "ours_wins": 73,
        "ties": 512,
        "coverage": 1.0
      }
    },
    "peptide_length_outliers_on_reference_short": {
      "nine_sample_mean": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.003824981136772283,
        "theirs": 0.0033665559899467502,
        "theirs_minus_ours": -0.00045842514682553224,
        "ci95": [
          -0.0008183147446520092,
          -0.00010253820881049057
        ],
        "ours_wins": 256,
        "ties": 283,
        "coverage": 1.0
      },
      "three_sample_medoid_expectation": {
        "n": 626,
        "clusters": 606,
        "bootstrap_unit": "cluster",
        "ours": 0.003624361588217782,
        "theirs": 0.0033665559899467502,
        "theirs_minus_ours": -0.00025780559827103206,
        "ci95": [
          -0.0006076170882411291,
          8.849186266528962e-05
        ],
        "ours_wins": 132,
        "ties": 407,
        "coverage": 1.0
      }
    }
  },
  "eligible_for_new_noise_pool": false,
  "accuracy_promotion": false,
  "oracle_tm_only": 0.6061431309904154,
  "selection_seconds": 59.272020778036676,
  "existing_generation_seconds_by_trio": [
    481.79933617729694,
    477.2283926648088,
    478.41156639996916
  ],
  "head_decoder_sample_budget_multiplier": 3,
  "additional_gpu_hours": 0,
  "final_test_scored": false
}
```
