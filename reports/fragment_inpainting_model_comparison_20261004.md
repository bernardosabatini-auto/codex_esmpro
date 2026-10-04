# Fixed-fragment coordinate-inpainting diagnostic

Repeated32training-protein diagnostic; coordinate-decoder conditioning trained on original512 proteins. Not independent generalization. All128samples/arm and8designs/sample retained. Same valid refold must satisfy motif/global/scaffold gates. Native budgets reused unchanged; teacher RNG not claimed paired. Bootstrap describes family variation, not training-seed replication. Qualification permits a separate development assay only.

|Arm|Raw /128|Strong /128|Designable /128|Successful families|
|---|---:|---:|---:|---:|
|parent6000|25|8|45|7|
|generated_cond|97|7|36|6|
|generated_untrained|63|3|12|3|

Development-screen qualification: {"generated_cond": false}

generated_untrained minus parent6000, strict success: {'mean': -0.0390625, 'ci95': [-0.078125, -0.0078125], 'families': 32}

generated_cond minus parent6000, strict success: {'mean': -0.0078125, 'ci95': [-0.0390625, 0.015625], 'families': 32}

generated_cond minus generated_untrained, strict success: {'mean': 0.03125, 'ci95': [0.0, 0.0703125], 'families': 32}

## Verdict

Close this fixed2000-update recipe. Training improves on untrained clamping (7 versus3 strict successes;36 versus12 designable) but does not beat the original parent (8 strict;45 designable;7 families). The trained-parent strict difference is−0.78 percentage points, family-bootstrap interval−3.91 to+1.56; this is not evidence of improvement.

The more serious failure is physical:0/128 trained and0/128 untrained raw backbones have both supplied-fragment junctions intact, compared with128/128 parent backbones. The seven qualifying trained refolds do have intact junctions, so some arrangements are realizable, but the generator itself produces disconnected fragments. Coarse validity97/128 must not be presented as intact-chain validity.

Teacher/refold budgets are unchanged:2,048 new folds and1,024 parent folds reused; all arrays and same-refold outcomes independently audited. Trained and parent share6 strict outputs; training adds1 and loses2. There is only one pair of strict successes per arm, insufficient for a useful-diversity improvement claim; raw pairwise scaffoldTM remains about0.169.

The separately specified frozen3-versus10-step diagnostic50351369 passed104 numerical controls. Tensteps yields only1/128 connected generated backbones and6/128 connected native controls; its follow-up gate fails. Native known-path predictions also miss junctions at t0.9 despite low global coordinate error. No sampling-step extension or refolds for this diagnostic.

Next is a single matched test of junction-weighted coordinate flow matching, emphasizing full atoms in four scaffold residues on each side of the fixed motif while keeping all other training and sampling settings unchanged. Its gate explicitly requires connected raw backbones and connected same-refold successes.
