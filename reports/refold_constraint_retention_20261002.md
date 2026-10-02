# Constraint retention after sequence design and refolding

Exploratory stricter CPU analysis of existing complete assays; no new GPU sampling or thresholds tuned. Requires the same one of8designed sequences to have refold scTM>.5, valid full-backbone geometry and contact error/motif dRMS<=1A. Strict joint additionally retains the original generated-backbone joint gate; no failed raw output is rescued.

contact
[
  {
    "mode": "guided",
    "n": 8,
    "original_joint": 4,
    "strict_joint": 2,
    "any_refold_constraint_designable": 2
  },
  {
    "mode": "initial",
    "n": 8,
    "original_joint": 0,
    "strict_joint": 0,
    "any_refold_constraint_designable": 0
  },
  {
    "mode": "random",
    "n": 8,
    "original_joint": 3,
    "strict_joint": 3,
    "any_refold_constraint_designable": 3
  }
]

motif
[
  {
    "mode": "full_context",
    "n": 8,
    "original_joint": 3,
    "strict_joint": 0,
    "any_refold_constraint_designable": 0
  },
  {
    "mode": "isolated",
    "n": 8,
    "original_joint": 2,
    "strict_joint": 0,
    "any_refold_constraint_designable": 0
  }
]

Four-family feasibility panels only; this still does not establish experimental function or one-sequence multistability.
