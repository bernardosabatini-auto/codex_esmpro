# Fragment sequence-design diagnosis

Exploratory failure diagnosis, not a validated selection policy or training labels.32shared families/arm/task; samples are dependent. Motif NLL is reconstructed from four-decimal whole-chain and redesigned-region scores. Correlations are descriptive, with no significance claim.

|Task|Arm|Median unique /8|Scaffold sequence identity|Scaffold NLL|Motif NLL|Designable at1/2/4/8 attempts /32|
|---|---|---:|---:|---:|---:|---|
|c20|broad_balanced|8|0.628|1.218|2.794|3/6/7/8|
|c20|broad_weight3|8|0.624|1.206|2.777|4/4/5/5|
|c20|control_balanced|8|0.636|1.174|2.855|7/11/11/15|
|c20|control_weight3|8|0.651|1.173|2.862|7/9/11/14|
|f30|broad_balanced|8|0.635|1.238|2.599|1/1/2/4|
|f30|broad_weight3|8|0.646|1.214|2.573|2/2/2/3|
|f30|control_balanced|8|0.647|1.205|2.564|4/4/5/8|
|f30|control_weight3|8|0.641|1.223|2.599|4/6/7/9|

All arms have a median of eight distinct designs and scaffold pairwise sequence identity around0.62–0.65. Duplicate designs do not explain the loss. Fixed-motif NLL has weak, inconsistent descriptive associations with valid refold TM; it is not supported as a new training objective by this diagnostic. Scaffold NLL correlates modestly with refold TM but is not a validated surrogate. No temperature or attempt-budget sweep is justified by duplicates.
