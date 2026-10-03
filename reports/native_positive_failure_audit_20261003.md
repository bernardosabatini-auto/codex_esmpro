# Coverage failure: existing-control diagnosis

Post hoc numerical/mechanistic audit of three previously chosen historical controls that are also qualified training positives. No new target selection, samples, refolds, checkpoint choices, or generalization claim. Conditioning versus null measures responsiveness; raw geometry alone does not establish designability. Native projection audit measures latent changes only, not decoded coordinate equivalence.

|Step|Condition|Training proteins|Samples|Raw successes|Mean motif CA RMSD|Mean motif dRMS|
|---|---|---:|---:|---:|---:|---:|
|0|conditioned|3|12|0|2.163|1.239|
|0|null|3|12|0|7.760|7.117|
|400|conditioned|3|12|0|2.527|1.517|
|400|null|3|12|0|7.760|7.117|

Across all 52 qualified endpoint latents, terminal normalization changes any component by at most 1.2397766e-05. This excludes a large normalization mismatch in the reference endpoints; it does not test every sampler failure mechanism.
