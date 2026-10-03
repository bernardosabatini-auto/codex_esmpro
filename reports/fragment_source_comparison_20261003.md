# Training-source designability calibration

Training-only source calibration. Both cohorts use eight fixed20-motif designs per backbone. No generated/evaluation target labels. Source quality is not generator performance.

|Source corpus|Valid global refold /64|Same valid motif + global + scaffold /64|
|---|---:|---:|
|original512|57|50|
|added7429|57|44|

scaffold_joint_success: added minus original -0.094; 95% interval [-0.25, 0.0625].

valid_designable: added minus original 0.000; 95% interval [-0.109375, 0.109375].
