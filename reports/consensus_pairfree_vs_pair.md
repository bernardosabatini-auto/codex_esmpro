# Selected pair-free versus selected pair model

Deployment comparison of separately trained checkpoints. Not a causal architecture ablation. No matched end-to-end throughput claim.

| Metric | Pair | Pair-free | Pair-free minus pair [95% cluster CI] |
|---|---:|---:|---|
| tm_fixed_reference | 0.57367 | 0.56230 | -0.01137 [-0.015147973282604235, -0.0076324505188492394] |
| ca_lddt | 0.67836 | 0.67141 | -0.00695 [-0.009600869697791349, -0.004351987580328093] |

Development noninferiority against the selected pair model: False.

```json
{
  "status": "complete",
  "reference_selection_sha256": "118c6c24a825519957da36801aa2e3f39414c344b083376daf39eb08649ff54a",
  "candidate_selection_sha256": "05cdfcbc4408279d2220bb49ec54279db999d35a5ebe579efe49dfa8841ff525",
  "paired": {
    "tm_fixed_reference": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.5736656549520767,
      "theirs": 0.5622997923322683,
      "theirs_minus_ours": -0.011365862619808308,
      "ci95": [
        -0.015147973282604235,
        -0.0076324505188492394
      ],
      "ours_wins": 372,
      "ties": 0,
      "coverage": 1.0
    },
    "ca_lddt": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.6783631452277615,
      "theirs": 0.67141220993641,
      "theirs_minus_ours": -0.00695093529135162,
      "ci95": [
        -0.009600869697791349,
        -0.004351987580328093
      ],
      "ours_wins": 368,
      "ties": 0,
      "coverage": 1.0
    }
  },
  "geometry": {
    "predicted_ca_gaps_on_reference_short": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.0015674008886971018,
      "theirs": 0.0013900875692944117,
      "theirs_minus_ours": -0.00017731331940268997,
      "ci95": [
        -0.0005461983670801513,
        0.0001753338673636346
      ],
      "ours_wins": 55,
      "ties": 521,
      "coverage": 1.0
    },
    "peptide_length_outliers_on_reference_short": {
      "n": 626,
      "clusters": 606,
      "bootstrap_unit": "cluster",
      "ours": 0.0034633613804702043,
      "theirs": 0.0032324493065632163,
      "theirs_minus_ours": -0.00023091207390698709,
      "ci95": [
        -0.000836360848897426,
        0.00038442402721854634
      ],
      "ours_wins": 100,
      "ties": 430,
      "coverage": 1.0
    }
  },
  "development_noninferiority": false,
  "note": "Deployment comparison of separately trained checkpoints. Not a causal architecture ablation. No matched end-to-end throughput claim."
}
```
