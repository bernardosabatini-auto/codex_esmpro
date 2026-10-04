# Junction-weighted versus uniform coordinate training

All128samples/arm,32training proteins; identical initialization and2000non-loss draws. Uniform and weighted training losses are different objectives and cannot be directly compared. No designability claim from geometry. Failure closes this fixed weighting recipe; no duration/window/weight sweep.

|Arm|Loss|Coarse valid|Both junctions|Connected motif+geometry|All flank edges intact|Median boundary C–N Å|
|---|---|---:|---:|---:|---:|---:|
|generated_cond|uniform|97|0|0|0|4.317|
|generated_cond|weighted|90|1|1|1|3.867|
|generated_null|uniform|3|0|0|0|7.468|
|generated_null|weighted|0|0|0|0|7.905|
|generated_untrained|uniform|63|0|0|0|6.042|
|generated_untrained|weighted|63|0|0|0|6.042|
|native_cond|uniform|122|2|2|1|2.068|
|native_cond|weighted|113|15|15|14|1.746|
|native_direct|uniform|128|127|127|127|1.352|
|native_direct|weighted|128|127|127|127|1.352|
|native_null|uniform|0|0|0|0|7.795|
|native_null|weighted|0|0|0|0|7.936|
|native_untrained|uniform|57|0|0|0|6.110|
|native_untrained|weighted|57|0|0|0|6.110|
|parent|uniform|128|128|25|128|1.342|
|parent|weighted|128|128|25|128|1.342|

All counts are out of128. Refold eligibility: {'qualified': False, 'connected_raw': 1, 'required': 45}

Paired2000-update draws verified; profile/full first40 parameter max difference: 0.0.


Verdict: close this fixed weighting recipe. Do not refold, extend or sweep it.
The next bounded question is CPU-only local backbone closure while keeping all supplied
motif atoms and the far scaffold fixed. Geometry targets come only from the corresponding
parent-generated backbone. The feasibility plan is recorded in
`configs/fragment_local_closure_feasibility.json`; objective coefficients and solver caps
must be fixed before real outputs. Successful closure would still require a separate
same-valid-refold designability assay and a matched untrained-clamp closure control.
