# Nonbonded backbone diagnostic

Posthoc diagnostic of nonbonded atom distances below1.5A, excluding pairs within three covalent bonds, touching16editable residues. No native scaffold/sequence enters deployment. Not a replacement of historical gates.

```json
[
  {
    "arm": "generated_cond",
    "subset": "all",
    "samples": 128,
    "candidate_overlap_cases": 77,
    "parent_overlap_cases": 1,
    "physical_and_overlap_free": 40
  },
  {
    "arm": "generated_cond",
    "subset": "profile",
    "samples": 16,
    "candidate_overlap_cases": 7,
    "parent_overlap_cases": 1,
    "physical_and_overlap_free": 9
  },
  {
    "arm": "generated_cond",
    "subset": "physical",
    "samples": 61,
    "candidate_overlap_cases": 21,
    "parent_overlap_cases": 0,
    "physical_and_overlap_free": 40
  },
  {
    "arm": "generated_cond",
    "subset": "designable",
    "samples": 20,
    "candidate_overlap_cases": 4,
    "parent_overlap_cases": 0,
    "physical_and_overlap_free": 15
  },
  {
    "arm": "native_cond",
    "subset": "all",
    "samples": 128,
    "candidate_overlap_cases": 0,
    "parent_overlap_cases": 0,
    "physical_and_overlap_free": 124
  },
  {
    "arm": "native_cond",
    "subset": "profile",
    "samples": 16,
    "candidate_overlap_cases": 0,
    "parent_overlap_cases": 0,
    "physical_and_overlap_free": 16
  },
  {
    "arm": "native_cond",
    "subset": "physical",
    "samples": 124,
    "candidate_overlap_cases": 0,
    "parent_overlap_cases": 0,
    "physical_and_overlap_free": 124
  },
  {
    "arm": "native_cond",
    "subset": "designable",
    "samples": 0,
    "candidate_overlap_cases": 0,
    "parent_overlap_cases": 0,
    "physical_and_overlap_free": 0
  }
]
```
