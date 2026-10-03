# Broader fragment training: final verdict

Expanding from512 to7941 proteins improved raw motif retention but failed to improve validated scaffold generation. Equal motif/scaffold loss weighting did not rescue it. Do not extend or promote these candidates.

All four matched2000-update extensions completed8000 total updates. Initial outputs and every training trace matched where prescribed. Both motif tasks used the same64 development families, four noises per family, eight fixed-motif designs per evaluated backbone, and a prospectively fixed32-backbone designability panel. These are development results, not independent-test estimates.

|Motif task|Arm|Raw retained /256|Same valid motif + global + scaffold /256|Fixed-panel global designability /32|
|---|---|---:|---:|---:|
|c20|control_weight3|22|6|14|
|c20|control_balanced|17|4|15|
|c20|broad_weight3|50|6|5|
|c20|broad_balanced|45|5|8|
|f30|control_weight3|30|1|9|
|f30|control_balanced|28|1|8|
|f30|broad_weight3|46|0|3|
|f30|broad_balanced|43|0|4|

The4000 new refolds covered all raw matches plus the prespecified designability panel;1024 historical native-control attempts were reused unchanged. A successful sample required one valid refold satisfying both motif limits, global TM>0.5, and scaffold-only TM>0.5. Raw failures remain in denominators.

Broader-label geometric feasibility was high:7429/7429 new central20-residue motifs survived their stored target roundtrip within1A, but this did not predict generator designability.

Next: training-only source calibration on64 original and64 added structures,16 per length bucket per cohort. Selection ignores confidence and refold outcomes. Exactly eight fixed20-residue-motif ProteinMPNN sequences per source, with identical teacher settings. This separates poor training-source designability from learning failure; it is not a further training sweep.
