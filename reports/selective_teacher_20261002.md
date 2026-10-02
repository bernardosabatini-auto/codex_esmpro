# Reference-free teacher fallback diagnostic

All626 repeatedly used development targets; no held-out claim. Student is the existing3sample medoid, teacher is fixed sample0.157teacher calls for both disagreement and length policies, frozen before reference scores. No new GPU inference and no end-to-end speed claim.

| Policy | TM | Change vs student [95%cluster CI] |
|---|---:|---|
| student | 0.57367 | +0.00000 [0.0, 0.0] |
| disagreement25 | 0.58343 | +0.00976 [0.005231257663232019, 0.014882325401572109] |
| length25 | 0.58496 | +0.01130 [0.007543425652420551, 0.015399970072282419] |
| random25_expectation | 0.57989 | +0.00623 [0.00431591361198184, 0.0080822264373807] |
| teacher | 0.59849 | +0.02482 [0.017208674656691923, 0.03222594745095745] |

Disagreement relative to equal-budget alternatives:
{'delta': -0.001537587859424921, 'ci': [-0.006109488957067681, 0.003442171688745975]}
{'delta': 0.0035362243413732913, 'ci': [-0.00018739091187626645, 0.007649918563412304]}

TM-based correlations:
{
  "all": {
    "n": 626,
    "spread_vs_student_error": 0.8238910406473855,
    "spread_vs_teacher_benefit": 0.09264860940475494
  },
  "short": {
    "n": 459,
    "spread_vs_student_error": 0.8171244368644138,
    "spread_vs_teacher_benefit": 0.08206701868107924
  },
  "long": {
    "n": 167,
    "spread_vs_student_error": 0.8703027324523965,
    "spread_vs_teacher_benefit": 0.0629970217829193
  },
  "length_adjusted": {
    "spread_vs_student_error": 0.8378321814021269,
    "spread_vs_teacher_benefit": 0.027285102149079938
  }
}

A correlation with student error is not calibration or proof of teacher benefit. Cost must include all3student samples plus selected teacher calls. No threshold tuning, oracle sample choice, independent tests or retraining.
