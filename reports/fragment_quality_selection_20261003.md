# Matched fragment-quality selection

CPU preparation only. Subsequent paired training must use identical parent, frozen-generator policy, protein/noise/time/dropout/LR draws, condition count and length/placement frequencies. Record expected condition-identity differences explicitly. Both arms restrict training to one20-residue fragment per protein, so comparisons to earlier12-condition recipes are descriptive only. Training-source confidence can covary with fragment structure and sequence; do not claim a pure confidence effect. No evaluation labels enter this selection.

Feasibility qualified: True. Mean confidence gain: 11.354.

|Length bucket|Proteins|Control mean|Quality mean|Gain|Changed conditions|
|---|---:|---:|---:|---:|---:|
|128|2045|86.17|92.35|6.18|1370|
|256|2026|82.26|91.78|9.53|1344|
|384|1956|72.80|87.58|14.78|1305|
|512|1914|71.84|87.15|15.31|1279|
