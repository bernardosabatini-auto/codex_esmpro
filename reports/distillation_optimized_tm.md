# Optimized fixed-correspondence TM accuracy

All 64 tuning families, three samples, all four arms at 0/500/2000. No checkpoint selection or test scoring.

USalign optimizes the rigid fit while retaining the verified residue correspondence. AFDB reference structures are predictions. This supplements the separately reported Kabsch-based score; it does not replace or alter the state-coverage gate.

| Arm | Updates | Mean TM | Change from own initialization | 95% family interval | Change from canonical reference | 95% family interval |
|---|---:|---:|---:|---|---:|---|
| balanced | 500 | 0.68263 | -0.00225 | [-0.00736, +0.00325] | +0.00296 | [-0.00046, +0.00625] |
| balanced | 2000 | 0.68282 | -0.00206 | [-0.00794, +0.00406] | +0.00479 | [+0.00104, +0.00865] |
| empirical | 500 | 0.68298 | -0.00189 | [-0.00756, +0.00413] | +0.00331 | [+0.00069, +0.00605] |
| empirical | 2000 | 0.68409 | -0.00079 | [-0.00708, +0.00588] | +0.00606 | [+0.00194, +0.01053] |
| raw_reference | 500 | 0.67939 | -0.00548 | [-0.01197, +0.00108] | -0.00028 | [-0.00485, +0.00372] |
| raw_reference | 2000 | 0.68361 | -0.00127 | [-0.01077, +0.00805] | +0.00558 | [-0.00003, +0.01163] |
| reference | 500 | 0.67967 | -0.00520 | [-0.01143, +0.00140] | +0.00000 | [+0.00000, +0.00000] |
| reference | 2000 | 0.67803 | -0.00684 | [-0.01413, +0.00034] | +0.00000 | [+0.00000, +0.00000] |
