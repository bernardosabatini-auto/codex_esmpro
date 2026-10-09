# Physical closure did not improve designability

All1,024new sequence/refold attempts completed across four RTX jobs. The matched
comparison reuses four distinct original parent partitions and the original
experimental controls. No replacement sequences or filtered backbones were added.

| Outcome /128 | Original parent | Torsion closure |
|---|---:|---:|
| Same-refold strict successes |8|8|
| Families with strict success |7|6|
| Ordinary valid designability |45|20|
| Connected designability |43|16|
| Complete raw geometry plus connected designability |43|14|

Closure retained4strict successes, gained4and lost4. It retained19designable cases,
gained1and lost26. The paired family-bootstrap designability difference is−19.53
percentage points,95% interval[−28.13,−11.72]. Geometry alone was misleading.
The fixed recipe fails every advancement criterion. Do not use its geometry-only
successes as positive designability labels, expand it, or claim a learned-model gain.

A posthoc diagnostic found73/128outputs with nonlocal backbone atom pairs below1.5Å,
versus1/128parents. Including adjacent residues but excluding all pairs within three
covalent bonds raises the count to77/128;21of61geometry-qualified cases contain
these overlaps. Native controls have none. The CA-only clash loss misses atomic
contacts. Median phi/psi change is45.52°overall,21.56°among designable outputs and
48.14°among failures. These associations do not prove causation.

## Targeted CPU test

A prospectively fixed atom-repulsion term was added with unchanged endpoints,
initialization, torsion window and iteration budget. Gradient, covalent-exclusion,
fixed-atom, repeatability and proper-pose controls pass. The32-output profile completed
in147.57s: generated complete geometry12/16, overlap-free complete geometry11/16
versus9/16previously; native16/16. Independent saved-torsion replay reproduced all32
outputs exactly and confirmed every score. It missed the predeclared12/16threshold. No full
expansion or refolds are launched for this recipe. All failed outputs are retained.

The next paired CPU hypothesis is prescribed in
`configs/movable_motif_closure_protocol.json`: allow the rigid isolated motif to
translate/rotate jointly with torsion closure, against an otherwise identical
fixed-pose control. The original placement is only a least-squares fit to a generated
parent; its absolute position is not part of the supplied isolated-fragment constraint.
Its arbitrary fixation may force strain. Preserve motif shape and distant scaffold;
do not transform8-channel latents as if they were3D vectors.

## Resource and monitoring audit

Jobs50392677,50392728,50392771and50392833 finished successfully in12:40,11:24,
13:10and11:39, respectively:0.815allocated GPU-hours total. Peak memory29.64GiB;
captured composite utilization42.06%over2,809seconds. These captures exclude startup
and do not reproduce the account24-hour dashboard. CPU scoring wait totaled7.21s.
Teacher/input content was verified on CPU before GPU allocation.

On resumption, the watcher was stalled in a shared-filesystem lock and an archive
reader reproduced the same stall. Only the identified own processes were stopped.
Watcher and submission locks now use distinct project-specific local-runtime files
and enforce the configured owner host. A fresh successful heartbeat was verified.
Completed immutable HDF5 archives were read without shared-file locks, with content
hash checks intact. No other agents' jobs or services were inspected or changed.

Evidence: `torsion_refold_comparison_20261008.json`,
`torsion_nonbonded_diagnostic_20261008.json`, `steric_torsion_profile_20261008.json`.
