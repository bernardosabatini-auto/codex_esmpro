# Native-anchor pilot interpretation

On the repeated 32-protein training diagnostic, the parent scored 8/128 strong successes and 45/128 designable outputs over 7 successful families; positive-only training for 400 updates scored 9/128 and 51/128 over 6 families; contrastive training scored 9/128 and 56/128 over 6 families. All 2,048 new refolds and all numerical controls completed. Both prespecified development gates failed; retain the 6,000-update parent.

Contrastive designability versus the parent increased 8.59 percentage points (paired family bootstrap 95% interval: 3.125 to 14.844 points). The contrastive-minus-positive interval includes zero. Strict success differences versus the parent and between trained arms remain unresolved. This is training-only evidence, not independent generalization or training-seed replication.

Raw-failure / no-valid-global / global-without-motif / joint-without-scaffold / strong counts:

|Arm|Raw failure|No global|Motif lost|Scaffold failed|Strong|
|---|---:|---:|---:|---:|---:|
|Parent|103|11|4|2|8|
|Positive|103|11|5|0|9|
|Contrastive|97|11|8|3|9|

The contrastive raw-retention gain did not become a comparable joint-success gain. All-pair structural diversity remained similar: mean global pair TM 0.18261 for the parent, 0.18185 positive-only, and 0.18476 contrastive. There were only 1/3/4 pairs of jointly successful samples, respectively; this is insufficient for a broad useful-diversity claim.

A retrospective feasibility check of the separate 16-source anchor calibration (refold jobs 50196541, 50196624, 50196745, 50196830) found 6/64 raw matches, only 1 output that was both a raw match and designable, and one negative whose valid global/scaffold refolds lose the motif in BOTH design halves: AF-A0A7Z9IM02-F1-model_v6, generation slot 1. Do not train a hard-negative objective from that single case.

Next hypothesis: the ten verified positive anchors give insufficient conditioning coverage. The fixed protocol in configs/native_positive_coverage_protocol.json selects 64 fresh training sources without examining outcomes, qualifies two decoded-reference realizations per source using the same valid refold, then permits a 400-update positive-only data-coverage experiment only if all calibration/profile gates pass. This isolates verified-positive coverage, using the completed ten-anchor positive-only run as its matched control. It does not promote either failed pilot or relax the strict endpoint.

One CPU audit exceeded its original 240-second allowance; its GPU run succeeded. The failure remains in watcher events. CPU audits now have a bounded 900-second allowance, locked hash-checked report reuse, and at most one expensive watcher audit per tick. Independent completed partitions were scored in parallel. Late CPU diversity completion also triggers the fixed comparison. No GPU jobs were rerun for the CPU timeout.

Inventory-only correction before new outcomes: excluding previous source/feedback cohorts leaves 8/151/142/142 available proteins in the four length buckets. The initial 16-per-bucket draft was infeasible and is preserved in runs/native_positive_coverage_original_inventory_draft_20261003.json. The fixed new panel uses 8/16/20/20 sources; later training retains the original equal bucket cycle. No model, decoder, or refold result informed this adjustment.
