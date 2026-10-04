# Full-context RePaint teacher feasibility

Status: complete.

Oracle training-label source, not isolated-fragment inference. All32 training proteins and128 outputs retained.

| Arm | Raw motif matches | Valid | Mean motif RMSD (A) |
|---|---:|---:|---:|
| oracle_repaint | 86/128 | 89/128 | 0.513 |
| parent | 25/128 | 128/128 | 2.252 |

Eight control groups passed, including16 historical outputs. Generation 102.92s; worker 166.17s; peak 6.80GiB.
Eligible for complete fixed-motif refolding: True. Designability not yet measured.

The teacher uses native-context motif codes. A better result cannot be attributed solely to architecture and would not prove an isolated-input student can reproduce it.

Teacher minus parent raw_gate_passed: +0.4766;95% family interval [0.375, 0.5703125].

Teacher minus parent coarse_valid: -0.3047;95% family interval [-0.3751953124999998, -0.2265625].

Teacher minus parent motif_ca_rmsd: -1.7387;95% family interval [-2.109356052197256, -1.3890351619065509].
