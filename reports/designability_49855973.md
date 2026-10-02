# Fixed-budget ProteinMPNN/refolding profile

Status: complete.

| Head | Mode | Backbones | Best8 scTM | Designable | Joint motif success | Refold s |
|---|---|---:|---:|---:|---:|---:|
| experimental | real | 4 | 0.9367 | 1.0000 | None | 30.40 |
| original50 | motif_u1 | 8 | 0.4173 | 0.3750 | 0.375 | 55.03 |
| original50 | motif_u3 | 8 | 0.6214 | 0.7500 | 0.75 | 55.11 |
| original50 | unconditional | 8 | 0.5879 | 0.7500 | None | 55.22 |
| reflow10 | motif_u1 | 8 | 0.3090 | 0.0000 | 0.0 | 54.90 |
| reflow10 | motif_u3 | 8 | 0.4152 | 0.2500 | 0.125 | 55.03 |
| reflow10 | unconditional | 8 | 0.4658 | 0.3750 | None | 54.97 |

4families/2samples profile, fixed-correspondence USalign, positive controls required; no independent-test or experimental-validation claim

Joint success means best8 scTM>0.5 AND motif distance-matrix RMS<=1A. Each backbone receives8designed sequences/8refolds; no rejection sampling. Timings include full guarded FP32 teacher folding and exclude CPU scoring; total elapsed and ProteinMPNN time retained in JSON. Motif codes derive from complete source backbones; separate designs do not demonstrate one sequence supporting multiple states. Every failure is retained.

All 416 refolds audited; ProteinMPNN 81.69s; total elapsed 517.29s.

Requiring the unchanged full-backbone coarse-validity gate as well:
- experimental real: valid and designable=1.0000, valid joint motif success=None.
- original50 motif_u1: valid and designable=0.1250, valid joint motif success=0.125.
- original50 motif_u3: valid and designable=0.5000, valid joint motif success=0.5.
- original50 unconditional: valid and designable=0.7500, valid joint motif success=None.
- reflow10 motif_u1: valid and designable=0.0000, valid joint motif success=0.0.
- reflow10 motif_u3: valid and designable=0.0000, valid joint motif success=0.0.
- reflow10 unconditional: valid and designable=0.2500, valid joint motif success=None.

Pairwise structural similarity (lower means greater diversity), with pair counts; sparse successful pairs cannot establish ensemble capacity:
- original50 motif_u1 all: pairs=4, mean fixed-correspondence TM=0.3440375.
- original50 motif_u1 valid_designable: pairs=0, mean fixed-correspondence TM=None.
- original50 motif_u1 valid_joint_motif_success: pairs=0, mean fixed-correspondence TM=None.
- original50 motif_u3 all: pairs=4, mean fixed-correspondence TM=0.35906249999999995.
- original50 motif_u3 valid_designable: pairs=1, mean fixed-correspondence TM=0.35277.
- original50 motif_u3 valid_joint_motif_success: pairs=1, mean fixed-correspondence TM=0.35277.
- original50 unconditional all: pairs=4, mean fixed-correspondence TM=0.17237000000000002.
- original50 unconditional valid_designable: pairs=2, mean fixed-correspondence TM=0.181085.
- reflow10 motif_u1 all: pairs=4, mean fixed-correspondence TM=0.3166125.
- reflow10 motif_u1 valid_designable: pairs=0, mean fixed-correspondence TM=None.
- reflow10 motif_u1 valid_joint_motif_success: pairs=0, mean fixed-correspondence TM=None.
- reflow10 motif_u3 all: pairs=4, mean fixed-correspondence TM=0.32644999999999996.
- reflow10 motif_u3 valid_designable: pairs=0, mean fixed-correspondence TM=None.
- reflow10 motif_u3 valid_joint_motif_success: pairs=0, mean fixed-correspondence TM=None.
- reflow10 unconditional all: pairs=4, mean fixed-correspondence TM=0.16994749999999997.
- reflow10 unconditional valid_designable: pairs=1, mean fixed-correspondence TM=0.17904.
- reflow10 minus original50, unconditional sc_tm: -0.1221, family interval [-0.250055, 0.005794999999999995].
- reflow10 minus original50, unconditional designable: -0.3750, family interval [-0.75, 0.0].
- reflow10 minus original50, motif_u1 sc_tm: -0.1083, family interval [-0.16432999999999998, -0.005428749999999982].
- reflow10 minus original50, motif_u1 designable: -0.3750, family interval [-0.5, -0.125].
- reflow10 minus original50, motif_u1 joint_motif_success: -0.3750, family interval [-0.5, -0.125].
- reflow10 minus original50, motif_u3 sc_tm: -0.2062, family interval [-0.37515624999999997, -0.048315].
- reflow10 minus original50, motif_u3 designable: -0.5000, family interval [-1.0, 0.0].
- reflow10 minus original50, motif_u3 joint_motif_success: -0.6250, family interval [-1.0, -0.25].
