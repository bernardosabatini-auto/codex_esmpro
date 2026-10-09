# Endpoint triangle diagnostic

Ghost endpoint N/CA/C uses parent internal lengths and angle, while the fixed requested motif has its own triangle. This rigid proper-fit RMSD is a nonzero lower bound irrespective of bridge torsions or motif rigid pose. It is an objective inconsistency, not evidence that current physical gates or designability would improve after changing it. Exact parent-equals-source identity controls cannot reveal this mismatch.

```json
[
  {
    "arm": "generated_cond",
    "samples": 128,
    "median_floor": 0.029950998875694156,
    "max_floor": 0.15845528595510056,
    "at_floor": 110,
    "floor_above_005": 28
  },
  {
    "arm": "native_cond",
    "samples": 128,
    "median_floor": 0.02058571522766639,
    "max_floor": 0.07382508601471485,
    "at_floor": 128,
    "floor_above_005": 7
  }
]
```
