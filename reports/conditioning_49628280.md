# Residual conditioning screen

Status: complete; arm: final.

Native-only conditioning screen. Frozen inherited flow/decoder; only bounded residual adapter learned. No teacher training or confirmation-set scoring.

512 reference-supervised training families; 64 tuning families, three fixed sampling seeds. Source structures are inherited AFDB predictions. Flow head and ProteinAE decoder stay frozen. Layer confirmation and original independent test are not scored here.

| Updates | Mean CA lDDT | Mean CA RMSD (A) |
|---|---:|---:|
| 0 | 0.78384 | 11.871 |
| 250 | 0.78339 | 11.862 |
| 500 | 0.78190 | 11.678 |

This is a single training-seed tuning screen. Promotion requires replication and matched ensemble/accuracy checks.
