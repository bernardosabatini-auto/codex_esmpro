# Movable motif: geometry improves, designability still fails

The full paired CPU assay retained all512outputs. Allowing the intact20residue
motif to translate/rotate increased generated physical-and-overlap-free cases
from60/128to77/128:23gained,6lost,54retained. Native controls stayed124/128.
All64profile outputs and512saved-parameter replays matched exactly. This is a
constructive geometry result, not learned capacity.

All128free-pose generated backbones then received eight original-motif-fixed
ProteinMPNN sequences and the unchanged deterministic FP32 ESMFold2-Fast assay.
Every failure remained in the denominator. Four distinct original parent
partitions and experimental-control budgets were reused unchanged. Parent raw
structures received the same atom-contact gate; their outcome counts stayed unchanged.

| Outcome /128 | Original parent | Movable motif |
|---|---:|---:|
| Same-valid-refold strict motif/global/scaffold/connectivity success |8|12|
| Strict families |7|9|
| Ordinary valid designability |45|25|
| Connected designability |43|24|
| Raw physical quality plus connected designability |43|23|

Strict success retained7, gained5and lost1; its paired family-bootstrap difference
is+3.125percentage points,95% interval[0,7.03125]. Ordinary designability retained20,
gained5and lost25:−15.625points,95% interval[−25,−7.03125]. Complete connected
designability retained18, gained5and lost25. The required45complete-connected
successes was missed by22. This fixed recipe is closed; do not promote it or train
on its geometry-only positives. No extension or replacement sequence draws.

Atomic cleanup did not resolve the problem. Among77physically eligible cases,
the original parents were designable31times and the constructions24times. Among
the51physical failures, the corresponding counts were14and1. Even a posthoc
geometry-only fallback to the original parent would give38/128ordinary designable
samples with these existing budgets, below45. This calculation diagnoses the
limitation; it is not a prospectively qualified selection algorithm.

The earlier full-context oracle RePaint teacher remains a stronger starting point:
13strict in9families and57designable, while its400-update isolated-input endpoint
student failed. Next investigate that transfer bottleneck before spending more on
local closure. Full-context motif latent codes are unavailable at deployment; any
student must receive only isolated geometry/sequence, length and insertion position.
Preserve the failed400-update recipe and distinguish a new conditioning objective
from a duration or threshold sweep. Do not treat contextual oracle inputs as deployable.

GPU jobs51458371/51458615/51458918/51459103all completed0:0. Total0.9081GPU-hours,
29.64GiB peak reserved memory,38.04%captured weighted utilization. CPU geometry took
2340seconds outside allocations; all scientific scoring ran after GPU release.
Timed refolding was unchanged relative to the previous assay; unexplained worker
overhead increased. Additional phase timers are implemented for future justified
refolding runs. See gpu_efficiency_update_20261009.md for accounting and capture scope.

Evidence: movable_motif_full_20261009.json, movable_motif_full_audit_20261009.json,
movable_motif_refold_comparison_20261009.json. Locked tests remain untouched.
