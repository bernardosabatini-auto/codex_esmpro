# Noise steering: matched designability

Status: complete.

All eight cases per method; four experimental controls passed; all224refolds audited. Joint success requires contact within1A of8A, full-backbone coarse validity, and best8scTM>.5.

| Method | Contact | Geometry | Designable | Joint | Generation s | s/joint success |
|---|---:|---:|---:|---:|---:|---:|
| initial | 0.000 | 1.000 | 0.750 | 0.000 | 3.49 | None |
| guided | 0.625 | 1.000 | 0.750 | 0.500 | 168.06 | 42.014426974230446 |
| random | 0.375 | 1.000 | 0.750 | 0.375 | 41.27 | 13.755598233702282 |

Generation costs include initial draws and optimization/random search; designability assay costs are separate. No equal-compute or experimental-validation claim. Four families provide a feasibility comparison, not a population rate.
ProteinMPNN seconds: 44.79; assay elapsed seconds: 288.35.

Pairwise diversity, retaining pair counts:
- initial all: 4 pairs; mean fixed-correspondence TM 0.17237000000000002.
- initial valid_designable: 2 pairs; mean fixed-correspondence TM 0.181085.
- initial joint_success: 0 pairs; mean fixed-correspondence TM None.
- guided all: 4 pairs; mean fixed-correspondence TM 0.206165.
- guided valid_designable: 2 pairs; mean fixed-correspondence TM 0.23027.
- guided joint_success: 1 pairs; mean fixed-correspondence TM 0.26138.
- random all: 4 pairs; mean fixed-correspondence TM 0.195975.
- random valid_designable: 3 pairs; mean fixed-correspondence TM 0.20826999999999998.
- random joint_success: 1 pairs; mean fixed-correspondence TM 0.29696.

Sparse successful pairs cannot establish ensemble diversity. Separate designed sequences do not establish multistability of one sequence.
