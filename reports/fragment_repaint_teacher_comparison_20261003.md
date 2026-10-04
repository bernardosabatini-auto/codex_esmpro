# Oracle RePaint teacher: same-refold feasibility

All128 outputs and1024 designs retained. Teacher uses native-context motif codes; this is not isolated-fragment inference.

| Arm | Raw | Strict | Designable | Successful families |
|---|---:|---:|---:|---:|
|parent6000|25|8|45|7|
|oracle_repaint|86|13|57|9|

Teacher-label pilot qualified: True. Overlap: {'shared': 4, 'teacher_only': 9, 'parent_only': 4}. Strict teacher-minus-parent contrast: {'mean': 0.0390625, 'ci95': [-0.0078125, 0.09375], 'families': 32}.

Repeated32training-protein oracle-label feasibility. Native-context motif codes are teacher-only information. Same valid refold must retain motif and agree globally and on scaffold. No student improvement, generalization or experimental claim.
