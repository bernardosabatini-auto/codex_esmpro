# Decoder-only loading qualification

The inference loader constructs the unchanged external decoder directly, skipping the training framework and unused encoder. Decoder state, scale, parameterization and steps match exactly. Fixed unpadded and padded CPU outputs are bitwise identical.

Fresh-process CPU loading: full loader 10.003 seconds; decoder-only 1.088 seconds. This is not a GPU-node speed benchmark. Historical GPU oracle replay remains mandatory in the next scientific run. Checkpoint bytes remain unchanged, and the original loader remains available for encoding work.

Decoder state SHA256: `61e226f79071f63ef92bf5d9659143acb55afbc5d55a516484ee051335149b76`.
