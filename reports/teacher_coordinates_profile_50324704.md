# Refolding without unused confidence outputs

Qualified: False.

Exact-settings coordinate parity: True. Timed GPU-worker reduction: 2.86%. Peak allocated GiB: {'full': 29.344247817993164, 'coordinates': 29.344247817993164}.

| Length bucket | Seconds saved |
|---|---:|
|128|1.40%|
|256|2.48%|
|384|2.60%|
|512|3.13%|

Eight archived training sequences; 64 folds including warmups, 24 timed per arm. Same FP32 kernels, seeds and sampling settings. Confidence outputs unused by designability assay. Not a new accuracy or designability experiment.
