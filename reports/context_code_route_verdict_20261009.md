# Context-code conditioning: learned distribution failed

The matched 805,256-parameter flows each trained for 2,000 updates on 464 families
and three isolated 20-residue placements. All 32 evaluation families and 16
validation families were excluded. Exact profile replay and numerical controls
passed, but validation loss did not establish a conditional advantage:
0.494 versus 0.502, paired difference −0.0082, 95% family interval [−0.0273, 0.0102].

Both generated-code arms produced **zero motif matches and only 2/128 valid
scaffolds**. The new sampler had omitted terminal per-residue normalization.
Correcting that interface in a separate four-family probe did not rescue it:
both arms stayed **0/16 valid**, while original and normalized native-code controls
both passed 14/16. All numerical replay controls passed. These recipes are closed;
no refolding or longer training follows from these results.

The next diagnostic uses intact native code sequences from other training
proteins. Searching only center fragments in 7,893 certified, eligible training
proteins found qualifying geometric neighbors for 8/32 queries. Searching all
1,838,166 contiguous 20-residue windows took 21.5 CPU seconds and found neighbors
within both 1 Å criteria for 15/32 queries, or 52/128 nearest-family slots.
No evaluation or validation donor families were allowed. This is geometric
availability, not a prediction of motif retention or designability.

A fixed four-query profile compares nearest versus randomly selected native
training codes under the same frozen RePaint sampler. Original oracle replays
and donor-self controls separate transfer failure from defective source codes.
Its protocol is `configs/retrieved_context_profile_protocol.json`. No new model
training is part of this baseline. Any useful result must still pass the original
same-valid-refold motif/global/scaffold and designability assay.

Short GPU probes had substantial initialization time: the normalization worker
took 151.5 seconds, with 60.4 seconds timed generation. The next probe records
imports, staging and each model load separately, and captures counters before
loading. It stages byte-verified weights into a private temporary directory on
the node, preserving numerical controls and deleting only its own copies. This
tests a practical loading improvement; no speedup is claimed in advance.
