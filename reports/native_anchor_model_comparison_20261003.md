# Native-anchor model diagnostic

Repeated32training-protein diagnostic; disjoint from16anchor-source proteins, not independent generalization. All128samples/arm and8designs/sample retained. Same valid refold must satisfy motif/global/scaffold gates. Native budgets reused unchanged; teacher RNG not claimed paired. Bootstrap describes family variation, not training-seed replication. Qualification permits a separate development assay only.

|Arm|Raw /128|Strong /128|Designable /128|Successful families|
|---|---:|---:|---:|---:|
|parent6000|25|8|45|7|
|positive|25|9|51|6|
|contrastive|31|9|56|6|

Development-screen qualification: {"positive": false, "contrastive": false}

positive minus parent6000, strict success: {'mean': 0.0078125, 'ci95': [-0.0234375, 0.0390625], 'families': 32}

contrastive minus parent6000, strict success: {'mean': 0.0078125, 'ci95': [-0.03125, 0.0546875], 'families': 32}

contrastive minus positive, strict success: {'mean': 0.0, 'ci95': [-0.03125, 0.0390625], 'families': 32}
