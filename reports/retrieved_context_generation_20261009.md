# Intact native-code retrieval: generation prerequisite

The nearest-fragment arm passes the prespecified refolding prerequisite: 33/128 outputs retain the ORIGINAL query motif under both 1 Å criteria, and 86/128 pass coarse validity. Matched random native-code windows give 1/128 and 91/128. These are geometry results, not designability results.

The donor library contains 7,893 certified training proteins and 1,838,166 contiguous 20-residue windows. All 32 query families and 16 validation families are excluded from donors. Selection uses isolated fragment geometry, length bucket, and four distinct donor families. Intact full-context codes are copied without interpolation or rotation. The generator remains frozen. This is a retrieval-assisted baseline on a repeatedly used training-protein diagnostic, not an independently tested learned model.

Job51489000 preserved all32 query outputs and16 donor controls from the qualified profile. Sixteen fresh historical oracle outputs reproduced the original latents exactly, with identical geometry decisions. All failed query outputs remain in the denominator.

All128 outputs in each arm now receive the unchanged eight-design ProteinMPNN budget, fixing the ORIGINAL query sequence at the supplied fragment. Strict success requires motif retention, global agreement, and scaffold agreement in the same valid refold. The random arm is refolded in full despite its low raw motif count, to measure designability fairly. Original parent and native controls are reused unchanged. Connectivity is reported as an additional diagnostic. No geometry-only positive labels are admitted to training.

The frozen advancement rule requires more strict successes than both parent8 and random, at least seven successful families, and designability at least parent45 and random. A pass licenses replication or a separately specified student experiment; it does not establish a general improvement.

## Efficiency

Job51489000 completed in216 allocated seconds, using6.795GiB peak reserved memory. Worker time203.505seconds included192.736seconds of measured generation. Checkpoint staging1.372s, generator loading1.416s, decoder loading3.668s. The previous retrieval profile spent56.882s loading the decoder; the new loader skips unused encoder/training-framework construction while loading identical decoder tensors. CPU state/output equivalence and the GPU historical replay both passed. These loading observations came from different jobs and are not a controlled whole-job speedup benchmark.

On202 valid assigned-GPU one-second counter samples, SM active averaged78.89%, tensor active0%, DRAM active18.21%, and graphics engine active94.53%. The user's weighted composite is40.708%. Recording began before checkpoint loading; import/setup before recorder startup is excluded. This is not the account-wide24-hour metric. FP32 and the qualified scientific recipe are preserved.

Code and protocol: afd047f; generation worker frozen at7ef198f. Eighteen refolding, same-refold integrity, CPU scoring, and watcher tests pass. CPU provenance hashing precedes GPU allocation. Eight disjoint RTX requests of35minutes maximum cover2,048 new refolds; GPUs are released when each partition finishes.
