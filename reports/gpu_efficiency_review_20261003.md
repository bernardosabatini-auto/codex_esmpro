# GPU efficiency review

Recent runs have no valid SM/tensor/DRAM/GR counter capture. NVML busy time cannot establish the user's weighted Real GPU Utilization. Counters were disabled after Nsight reported a profiling conflict; no other process was inspected or stopped. The [KempnerPulse formula](https://github.com/KempnerInstitute/kempnerpulse/blob/main/docs/classification.md) uses bandwidth activity, not occupied VRAM. Historical allocation-normalized Nsight SM-issue percentages are also a different metric.

| Own run | Measured NVML GPU busy | Peak reserved memory | Worker elapsed |
|---|---:|---:|---:|
| Decoder adapter50293210 |91.5%|8.54GiB|871s|
| Full decoder50301053 |91.1%|37.01GiB|770s|
| Integration diagnostic50310363 |91.4%|5.68GiB|71s|
| RePaint teacher50313857 |97.8%|6.80GiB|166s|

All used RTX PRO6000 Blackwell with approximately95GiB visible memory. Busy percentages cover available NVML samples, which exclude some loading and validation time, not entire allocations. Small diagnostics have substantial startup cost; generation50313857 completed in188Slurm seconds with103seconds timed generation, plus controls/loading. This does not attribute the user's24-hour aggregate to this project or inspect other agents' jobs.

The representative256-refold parent partition50189270 spent609seconds in timed refolding,71seconds in ProteinMPNN, and740seconds total worker time. GPU busy averaged81.5% over733NVML samples; peak NVML memory was30.36GiB. CPU alignment and metric calculations currently serialize between GPU calls.

Implemented optional bounded CPU scoring overlap: one CPU worker, at mostfour outstanding records, strict output order and exception propagation. GPU model, FP32 policy, feature generation, RNG seeds, sequence budget, and refolding calls remain unchanged. Four historical records spanning all length buckets reproduce exactly under asynchronous scoring. New tests cover ordering, bounded background execution and failure propagation. This is an overhead improvement candidate, not a measured speedup yet.

The first new RePaint refolding partition will use CPU overlap and attempt scoped DCGM field1001/1002/1004/1005 capture on its assigned GPU only. A missing binary, unsupported counter or profiling conflict remains unavailable telemetry; it must not trigger profiler interference or invented utilization. Remaining partitions wait for this execution check. Future batch/concurrency changes require throughput and numerical qualification; allocating extra memory or extending runs solely to inflate utilization is not useful work.

## Verified counter sample

The initial direct-DCGM attempt in50315652 incorrectly used cgroup-local NVML index0; Slurm assigned physicalGPU4. That collector was stopped by selecting its PID from this exact registered job. The unverified capture is rejected and retained as a failure, never used for utilization claims. Replacement capture queried only the Slurm-assigned GPU and verified its UUID against the CUDA device. Future collection now performs registered-job lookup, scoped Slurm physical-index resolution, and UUID verification before starting DCGM; ambiguous mappings fail closed.

The replacement60-second window contains59valid rows and one unavailable startup row: SM active93.854%, tensor active0.575%, DRAM active50.210%, GR engine98.656%. The user's weighted composite is52.958%. This is one active-refolding interval, not full-allocation utilization or the user's24-hour dashboard statistic. FP32 helps explain low tensor-core activity; memory bandwidth and SM activity contribute most of the score. No precision change is needed merely to increase this number.

A CPU-only validation profile took14.52seconds, including8.76seconds hashing8.34GB across112calls/49unique files. Repeated hashing accounts for4.35GB; this is a smaller optimization opportunity than model/design throughput and is left unchanged to keep the current assay moving.

First overlapped partition50315652 completed0:0 in13:05. All256refolds, sequence checks and repeatability control passed independent scoring. Worker time738.06seconds; accumulated waits for CPU scoring1.63seconds. Historical partition50189270 took739.69worker seconds with different designed sequences/backbones, so this is not a controlled speedup estimate. The verified active-window composite is sufficient to retain current FP32 execution while completing the experiment.
