# Isolated-fragment RePaint endpoint student

Repeated32training-protein diagnostic; isolated-input adapter trained on13 selected labels in9 of these families, with23 other training families. Not independent generalization. All128samples/arm and8designs/sample retained. Same valid refold must satisfy motif/global/scaffold gates. Native budgets reused unchanged; teacher RNG not claimed paired. Bootstrap describes family variation, not training-seed replication. Qualification permits a separate development assay only.

|Arm|Raw /128|Strong /128|Designable /128|Successful families|
|---|---:|---:|---:|---:|
|parent6000|25|8|45|7|
|native_matched|20|4|49|4|
|repaint_positive|22|6|40|5|

Development-screen qualification: {"repaint_positive": false}

native_matched minus parent6000, strict success: {'mean': -0.03125, 'ci95': [-0.0703125, 0.0], 'families': 32}

repaint_positive minus parent6000, strict success: {'mean': -0.015625, 'ci95': [-0.0546875, 0.0234375], 'families': 32}

repaint_positive minus native_matched, strict success: {'mean': 0.015625, 'ci95': [-0.015625, 0.046875], 'families': 32}

## Decision

The fixed400-update RePaint-positive recipe failed its predeclared gate:6 strict successes in5 families and40 designable outputs, versus parent8/7/45 and matched-native4/4/49. The teacher-versus-parent strict difference is−1.56 percentage points, with family-bootstrap interval−5.47 to+2.34. This does not establish a population-level degradation, but it supplies no basis to expand or sweep this recipe. All2,048 new refolds passed numerical/inventory audits. No checkpoint, threshold or duration extension.

## Selected-label cohorts

|Arm|Cohort|Samples|Raw|Strict|Designable|
|---|---|---:|---:|---:|---:|
|parent6000|label_families|36|14|6|20|
|parent6000|other_training_families|92|11|2|25|
|native_matched|label_families|36|12|2|20|
|native_matched|other_training_families|92|8|2|29|
|repaint_positive|label_families|36|15|4|14|
|repaint_positive|other_training_families|92|7|2|26|

Even in the9 label families, teacher training raises raw matches14→15 but reduces strict successes6→4 and designability20→14 relative to the parent. The other23 training families retain2 strict successes. Raw motif fit was an inadequate proxy for the requested outcome.

## Strict-success diversity

|Arm|Pairs with both samples successful|Proteins|Mean scaffold TM|
|---|---:|---:|---:|
|parent6000|1|1|0.21226|
|native_matched|0|0|None|
|repaint_positive|1|1|0.19562|

The counts are too small to support a useful-diversity improvement claim. Teacher and parent share4 strict outputs; teacher adds2 and loses4. The matched-native control shares3 with the parent, adds1 and loses5.

Next: the prospective coordinate-inpainting protocol tests fixed supplied atoms inside the noisy coordinate state, with an untrained-clamp comparator. It is not implemented or GPU-qualified yet. Exact raw retention under clamping will not count as evidence of designability; the unchanged same-valid-refold assay remains primary.
