# ESMFold2-Fast adapter audit

The installed Transformers port does not respect `msa_encoder.enabled=false`.
The local Fast checkpoint lacks MSA encoder weights, but the generic feature
helper supplies a depth-one query MSA. The port builds MSA inputs whenever
`msa` is present and calls the newly initialized encoder inside every trunk loop.

This invalidates the earlier external baseline `49461971` and the new teacher
diagnostic `49619131` as scientific comparisons. A cancellation was requested
for the latter, but Slurm shows it had already completed in 3 minutes 42 seconds.
Its outputs are quarantined from evaluation and training. Numerical repeatability
alone did not detect the model-loading error; that was an inadequate control.

The corrected adapter supplies `msa=None`, verifies that all missing weights
belong exclusively to the disabled MSA module, and installs a runtime guard that
fails if that module executes. The no-MSA profile equals the query-only profile;
deletion features remain zero. No inherited environment or original source files
are modified.

The primary implementation constructs the MSA encoder only when enabled:
[Biohub source, pinned commit 43b4548](https://github.com/Biohub/esm/blob/43b4548b86762edfa747b07d5f440aad3c33acee/esm/models/esmfold2/model.py).
This establishes the intended disabled-module behavior; it does not establish
complete numerical equivalence of the HF port to Biohub's implementation.

The checkpoint also enables per-loop LM dropout during evaluation. Trunk reuse
therefore conditions on one stochastic trunk draw. The diversity experiment must
separate fixed-trunk diffusion seeds from multiple trunk seeds, and report their
different compute costs. Integration steps are not physical trajectory frames.

The corrected rerun `49626106` completed all 1,878 predictions on the same 626
development proteins. Mean fixed-correspondence TM is 0.599825 versus the
unchanged pair model's 0.568238. The earlier invalid-path result was 0.599770:
the correction had little effect on aggregate accuracy, but the new run is the
eligible baseline. The mean teacher advantage is 0.03159, with a family-bootstrap
95% interval of 0.02481–0.03863. No independent-test structures were scored.
