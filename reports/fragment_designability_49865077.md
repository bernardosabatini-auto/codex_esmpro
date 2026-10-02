# Isolated-fragment scaffolding designability

Status: complete.

All8fixed samples per method plus4experimental controls;160refolds audited. All positive and repeatability controls passed. Joint requires motif dRMS<=1A, full-backbone validity and best8scTM>.5.

| Codes | Motif dRMS A | Geometry | Designable | Joint |
|---|---:|---:|---:|---:|
| full_context | 0.390 | 0.625 | 0.625 | 0.375 |
| isolated | 0.409 | 0.250 | 0.375 | 0.250 |

Pairwise diversity with pair counts:
- full_context all: 4 pairs,mean fixed-correspondence TM 0.35906249999999995.
- full_context valid_designable: 1 pairs,mean fixed-correspondence TM 0.35277.
- full_context valid_joint_motif_success: 1 pairs,mean fixed-correspondence TM 0.35277.
- isolated all: 4 pairs,mean fixed-correspondence TM 0.3627425.
- isolated valid_designable: 1 pairs,mean fixed-correspondence TM 0.49019.
- isolated valid_joint_motif_success: 1 pairs,mean fixed-correspondence TM 0.49019.

MPNN 32.14s; assay elapsed 234.59s.

Four-family profile only; sparse successful pairs do not establish ensemble capacity. Separate sequence designs do not establish one-sequence multistability. No experimental validation, independent-test or end-to-end speed claim.
