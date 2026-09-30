# Backward profile

Status: complete

Profile draws are all conditioned, late time, and self-conditioned; capacity stress rather than representative training. Adam state and optimizer arithmetic are included; learning rate zero preserves checkpoint weights.

| Length | Arm | Batch | Proteins/s | Reserved GiB |
|---:|---|---:|---:|---:|
| 90 | flow | 32 | 53.02 | 14.50 |
| 90 | geometry | 32 | 46.20 | 14.75 |
| 170 | flow | 32 | 19.40 | 32.35 |
| 170 | geometry | 32 | 18.29 | 32.73 |
| 340 | flow | 32 | 5.58 | 106.41 |
| 340 | geometry | 32 | 5.45 | 106.42 |
| 394 | flow | 16 | 3.93 | 73.26 |
| 394 | geometry | 16 | 3.79 | 73.42 |

BF16 full-parameter gradient controls: [{"length": 90, "fp32_loss": 0.05728921294212341, "bf16_loss": 0.05745343491435051, "gradient_cosine": 0.9954626398609994, "relative_l2": 0.09552880796377614, "passed": true}, {"length": 170, "fp32_loss": 0.023392336443066597, "bf16_loss": 0.023613037541508675, "gradient_cosine": 0.9933386798725108, "relative_l2": 0.11523141241250223, "passed": false}, {"length": 340, "fp32_loss": 0.047354765236377716, "bf16_loss": 0.04814273491501808, "gradient_cosine": 0.9992153150107929, "relative_l2": 0.03993032597610846, "passed": true}, {"length": 394, "fp32_loss": 0.05719993636012077, "bf16_loss": 0.05790514126420021, "gradient_cosine": 0.9965220940034876, "relative_l2": 0.08344192213214086, "passed": true}]

Hardware: {"whole_capture_mean_percent": {"SMs Active [Throughput %]": 51.63304911323329, "SM Issue [Throughput %]": 33.561152796725786, "Tensor Active [Throughput %]": 0.6810027285129604, "DRAM Read Bandwidth [Throughput %]": 10.03993860845839, "DRAM Write Bandwidth [Throughput %]": 5.769167803547067}, "collection_mean_percent": {"SMs Active [Throughput %]": 82.64846863569362, "SM Issue [Throughput %]": 53.721078779276084, "Tensor Active [Throughput %]": 1.0900802533165912, "DRAM Read Bandwidth [Throughput %]": 16.003330239668067, "DRAM Write Bandwidth [Throughput %]": 8.775290713544795}, "capture_seconds": 293.189357418, "collection_seconds": 183.162169974, "counter_period_ns": 9999978.083086053, "validated_intervals": 1, "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."}
