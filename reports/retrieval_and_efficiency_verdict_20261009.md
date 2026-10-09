# Retrieval and GPU efficiency verdict

Intact-code retrieval is a useful mechanism control, but it failed the advancement rule. All2,048 new refolds and all128 generated outputs perarm were retained. Parent/native budgets were reused unchanged.

|Arm|Raw motif matches|Strict same-refold successes|Successful families|Designable|
|---|---:|---:|---:|---:|
|Original parent|25|8|7|45|
|Nearest native-code blocks|33|7|6|56|
|Random native-code blocks|1|0|0|48|

Retrieval beats random on strict success in this32-family diagnostic: paired difference0.05469, family-bootstrap95%interval[0.015625,0.1015625]. It does not beat the parent: difference−0.00781, interval[−0.05469,0.03906]. Its designability increase versus parent is uncertain: +0.08594,[−0.04688,0.22656]. This is a repeatedly used training-protein panel, not an independent benchmark.

Of33 raw retrieved motif matches,21 have a valid refold with global AND scaffold agreement; only7 also retain the original motif in that same refold. Conditioning works, but raw geometry overstates useful success. The additional connected-scaffold diagnostic is worse than parent:31versus43 complete connected designable cases; connected strict6versus8. One pair in one family has two strict successes, so successful diversity evidence is sparse.

Close this recipe. Do not increase sampling, label more retrieval examples, or treat raw geometric matches as positive training labels under this protocol.

## Efficiency

Across the eight scientific refolding jobs, the supplied four-counter composite averaged39.160% over6,055 complete assigned-GPU one-second samples. This includes recorded startup and excludes time before recorder startup; it is not the dashboard's hourly24-hour statistic. Individual jobs ranged34.27–43.44%. No other jobs were queried.

The decoder-only loader remains qualified: identical weights and CPU outputs, exact historical GPU replay, and measured GPU loading3.67s versus56.88s in the preceding retrieval profile. It skips the unused encoder/training framework.

Teacher checkpoint staging passed numerical checks but did not establish an efficiency improvement. In a warm-process probe, copying plus loading took21.82s versus29.15s for the first shared-storage load. A later shared-storage load took4.09s, exposing order/cache effects. The complete pipeline replay reproduced every one of256sequences and256refold backbones exactly, with identical decisions. Its copy39.44s plus load48.94s exceeded the historical load32.45s; worker time752.72s versus678.75s. Nodes/cache states differed, so neither difference is a controlled speedup estimate. Do not enable staging by default. The256replays add no scientific attempts.

CPU comparison audits now hash each immutable shared source once per invocation, checking its identity and expected digest at each reuse. This avoids repeated large-file reads without skipping initial content verification. Completed staging reports are reused without changing metadata bound by downstream jobs.

## Representation diagnostics

The whole-chain internal-coordinate primitive passes exactFP64 round trips, rigid-motion tests, prefix-product order tests, and finite-difference gradients. It reconstructs both chain halves around an unchanged motif without fixing distant atoms. In the36-output CPU profile, native controls retainTM1.0, but simple grafting leaves only6/16parent outputs coarse-valid and mean sourceTM0.553. Connectivity alone therefore remains insufficient. This result does not justify GPU training or a full graft assay.

The follow-up projected training-derived bond and angle bounds onto already conditioned decoder outputs, preserving torsions and the supplied motif. All16 generated cases became connected, but only2 retained joint physical validity; mean agreement with the starting structure fell toTM0.574. Native-conditioned outputs also failed (4/16 joint, meanTM0.628), while all4 genuine native controls retained validity andTM~1.0. These errors are not repaired by bond projection without disrupting packing. Close both CPU recipes; no GPU expansion or refolding.

A distinct hypothesis remains: apply decoded motif guidance during the flow trajectory, allowing later prior steps to adjust packing. Earlier initial-noise optimization, classifier-free guidance, and terminal latent correction do not test this intervention. Any pilot needs exact zero-guidance replay, derivative controls, a fixed schedule and strength, all failures retained, and a prospective validity gate before same-valid-refold testing. It is an inference experiment, not evidence of improved trained designability.
