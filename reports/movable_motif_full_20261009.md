# Full paired movable-motif CPU assay

Constructive feasibility; designability and learned capacity remain untested. All512outputs retained.

| Pose | Context | Physical /128 | Physical and overlap-free /128 | Families |
|---|---|---:|---:|---:|
| fixed_pose | generated_cond | 73 | 60 | 26 |
| fixed_pose | native_cond | 124 | 124 | 31 |
| free_pose | generated_cond | 85 | 77 | 29 |
| free_pose | native_cond | 124 | 124 | 31 |

Qualified: True; 2340.00 CPU seconds; no GPUs.
All64profile outputs repeated exactly. Original isolated fragment remains the scoring reference.

Paired physical-and-overlap-free changes:

```json
[
  {
    "arm": "generated_cond",
    "gained": 23,
    "lost": 6,
    "retained": 54
  },
  {
    "arm": "native_cond",
    "gained": 0,
    "lost": 0,
    "retained": 124
  }
]
```
