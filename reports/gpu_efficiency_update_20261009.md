# GPU efficiency: movable-motif refolds

Four registered own RTX jobs completed successfully:51458371,51458615,51458918,51459103. Total allocation3269seconds (0.9081GPU-hours). Peak PyTorch reserved memory29.64GiB. All1,024attempts retained.

Assigned-UUID DCGM capture:38.0351% weighted real utilization over3101valid one-second samples. SM active66.96%, tensor active0.37%, DRAM active33.47%. Captures exclude recorder startup and are not the account24-hour hourly-allocation metric.

| Worker timing, summed seconds | Previous torsion refolds | Movable motif |
|---|---:|---:|
| Total worker |2847.87|3162.15|
| Timed folds |2362.76|2366.96|
| ProteinMPNN stage |279.85|299.94|
| CPU scoring wait |7.21|8.00|
| Remaining worker time |198.05|487.25|

The remaining-time increase accounts for289.19of314.28additional worker seconds. It includes loading, initialization, file operations, repeatability controls and final checks; the old instrumentation cannot isolate those components. This is an observed cost comparison on matched length/budget panels with different designed sequences, not a controlled timing benchmark. Live manifests showed variable teacher-loading delays.

Input/teacher hashing and final scientific audits stayed on CPU outside allocations; scoring overlap remained enabled. Each GPU was released on worker completion. New lightweight import, preflight, CUDA/telemetry, backbone-export, MPNN-parse, teacher-load and final-file-check timers will identify avoidable overhead in the next justified refolding assay. They change no model, precision, seed, budget or sampling settings.
