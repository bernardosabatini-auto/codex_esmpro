# Retrieved native-code designability

Repeated training-protein diagnostic, not novel-protein generalization. Retrieval excludes all query and validation families. All128 outputs per arm, eight fixed-original-motif designs each; all failures retained. Strict success requires one valid refold with motif/global/scaffold agreement. Connectivity is an additional shared diagnostic, not a replacement endpoint. Parent uses different conditioning; retrieval versus random is the matched contrast. Donor rank and flow noise both vary across four slots. Qualification licenses a separate replication, not a learned-model claim.

|Arm|Raw|Strict|Designable|Strict families|Connected strict|
|---|---:|---:|---:|---:|---:|
|parent6000|25|8|45|7|8|
|retrieved|33|7|56|6|6|
|random|1|0|48|0|0|

Gate: {"strict": false, "families": false, "designability": true}

retrieved minus parent6000: {"raw_gate_passed": {"mean": 0.0625, "ci95": [-0.03125, 0.15625], "families": 32}, "scaffold_joint_success": {"mean": -0.0078125, "ci95": [-0.0546875, 0.0390625], "families": 32}, "valid_designable": {"mean": 0.0859375, "ci95": [-0.046875, 0.2265625], "families": 32}, "complete_strict": {"mean": -0.015625, "ci95": [-0.0625, 0.03125], "families": 32}, "connected_designable": {"mean": 0.09375, "ci95": [-0.03125, 0.234375], "families": 32}, "complete_connected_designable": {"mean": -0.09375, "ci95": [-0.234375, 0.046875], "families": 32}}

random minus parent6000: {"raw_gate_passed": {"mean": -0.1875, "ci95": [-0.265625, -0.109375], "families": 32}, "scaffold_joint_success": {"mean": -0.0625, "ci95": [-0.109375, -0.0234375], "families": 32}, "valid_designable": {"mean": 0.0234375, "ci95": [-0.15625, 0.203125], "families": 32}, "complete_strict": {"mean": -0.0625, "ci95": [-0.109375, -0.0234375], "families": 32}, "connected_designable": {"mean": 0.0390625, "ci95": [-0.1328125, 0.21875], "families": 32}, "complete_connected_designable": {"mean": -0.109375, "ci95": [-0.25, 0.03125], "families": 32}}

retrieved minus random: {"raw_gate_passed": {"mean": 0.25, "ci95": [0.140625, 0.3671875], "families": 32}, "scaffold_joint_success": {"mean": 0.0546875, "ci95": [0.015625, 0.1015625], "families": 32}, "valid_designable": {"mean": 0.0625, "ci95": [-0.0390625, 0.1640625], "families": 32}, "complete_strict": {"mean": 0.046875, "ci95": [0.0078125, 0.09375], "families": 32}, "connected_designable": {"mean": 0.0546875, "ci95": [-0.046875, 0.1484375], "families": 32}, "complete_connected_designable": {"mean": 0.015625, "ci95": [-0.0703125, 0.1015625], "families": 32}}
