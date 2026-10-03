# Native-anchor model diagnostic

Repeated32training-protein diagnostic; disjoint from16original and64new qualification sources. Not independent generalization. All128samples/arm and8designs/sample retained. Same valid refold must satisfy motif/global/scaffold gates. Native budgets reused unchanged; teacher RNG not claimed paired. Bootstrap describes family variation, not training-seed replication. Qualification permits a separate development assay only.

|Arm|Raw /128|Strong /128|Designable /128|Successful families|
|---|---:|---:|---:|---:|
|parent6000|25|8|45|7|
|positive|25|9|51|6|
|positive_coverage|23|7|48|5|

Development-screen qualification: {"positive_coverage": false}

positive minus parent6000, strict success: {'mean': 0.0078125, 'ci95': [-0.0234375, 0.0390625], 'families': 32}

positive_coverage minus parent6000, strict success: {'mean': -0.0078125, 'ci95': [-0.0390625, 0.0234375], 'families': 32}

positive_coverage minus positive, strict success: {'mean': -0.015625, 'ci95': [-0.0390625, 0.0], 'families': 32}
