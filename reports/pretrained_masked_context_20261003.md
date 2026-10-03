# Pretrained masked-flow context diagnostic

Post hoc paired diagnostic on32 repeatedly used training proteins,4fixed noises each. Bootstrap units are protein IDs; no independent generalization or training-seed replication claim. Native context supplies oracle scaffold information. Its advantage mixes context compatibility and model-distribution effects; it does not prove a motif physically impossible in a generated scaffold. Transition counts do not define a deployable selector. All original gates remain failed; no refolds were launched.

|Candidate minus reference|Raw difference|95% protein-bootstrap interval|
|---|---:|---|
|generated_cond minus parent|0.0000|[-0.0546875, 0.0546875]|
|generated_cond minus generated_null|0.1406|[0.0703125, 0.21875]|
|native_cond minus native_null|0.4062|[0.265625, 0.546875]|
|native_cond minus generated_cond|0.4375|[0.3125, 0.5625]|

Transitions: {"retained_raw": 14, "lost_raw": 11, "new_raw": 11, "native_raw_but_generated_failed": 59}

The pretrained repair retains much more valid geometry than the failed small model, but it does not improve raw motif coverage over the parent. A future experiment could test learned global scaffold adjustment; this is a hypothesis, not a rescue of the closed fixed-scaffold recipe.
