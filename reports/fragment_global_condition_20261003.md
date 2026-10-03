# Fragment global-conditioning audit

CPU only; same64 source-calibration training proteins, central20motifs and five fixed flow times. No development outcomes or refold scores used. Relative modulation changes diagnose routing magnitude, not causality or designability. No checkpoints selected.

|Arm|Pool delta RMS|Pool/time RMS|Pool/null+time RMS|Median block modulation change|Output modulation change|
|---|---:|---:|---:|---:|---:|
|parent6000|0.024|0.004|0.004|0.020|0.008|
|full512|0.023|0.004|0.004|0.020|0.009|
|full7941|0.025|0.005|0.005|0.019|0.008|
|frozen512|0.025|0.004|0.004|0.022|0.009|
|frozen7941|0.028|0.005|0.005|0.026|0.010|
