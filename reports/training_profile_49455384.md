# Backward profile

Status: complete

Profile draws are all conditioned, late time, and self-conditioned; capacity stress rather than representative training. Adam state and optimizer arithmetic are included; learning rate zero preserves checkpoint weights.

| Length | Arm | Batch | Proteins/s | Reserved GiB |
|---:|---|---:|---:|---:|
| 128 | flow | 128 | 69.44 | 39.65 |
| 128 | geometry | 128 | 66.48 | 40.01 |
| 256 | flow | 64 | 19.04 | 71.86 |
| 256 | geometry | 64 | 18.41 | 72.46 |
| 384 | flow | 32 | 8.57 | 80.57 |
| 384 | geometry | 32 | 8.24 | 80.63 |
| 512 | flow | 16 | 4.59 | 70.96 |
| 512 | geometry | 16 | 4.32 | 70.81 |

Candidate full-parameter gradient controls: [{"length": 90, "padded_length": 128, "fp32_loss": 0.057252801954746246, "candidate_loss": 0.057284947484731674, "candidate_precision": "fp16", "gradient_cosine": 0.9998652480909398, "relative_l2": 0.01642625119725625, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 0.04793520691461506}, {"length": 170, "padded_length": 256, "fp32_loss": 0.023393604904413223, "candidate_loss": 0.023379957303404808, "candidate_precision": "fp16", "gradient_cosine": 0.9998461270657794, "relative_l2": 0.01771512587178642, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 0.07532723170877606}, {"length": 340, "padded_length": 384, "fp32_loss": 0.04728097468614578, "candidate_loss": 0.047262512147426605, "candidate_precision": "fp16", "gradient_cosine": 0.9999342357341652, "relative_l2": 0.011516289054683658, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 2.1299151105121705}, {"length": 394, "padded_length": 512, "fp32_loss": 0.05720685422420502, "candidate_loss": 0.05724532529711723, "candidate_precision": "fp16", "gradient_cosine": 0.9998940224619021, "relative_l2": 0.014604841732061535, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 0.07224386787070494}]

Hardware: {"whole_capture_mean_percent": {"SMs Active [Throughput %]": 50.465239921932834, "SM Issue [Throughput %]": 22.4192745137627, "Tensor Active [Throughput %]": 3.3047647890167577, "DRAM Read Bandwidth [Throughput %]": 12.211992731677771, "DRAM Write Bandwidth [Throughput %]": 7.965340870852682}, "collection_mean_percent": {"SMs Active [Throughput %]": 82.87560786914236, "SM Issue [Throughput %]": 36.817583996463306, "Tensor Active [Throughput %]": 5.427221485411141, "DRAM Read Bandwidth [Throughput %]": 20.005249778956674, "DRAM Write Bandwidth [Throughput %]": 12.59775641025641}, "capture_seconds": 297.170486703, "collection_seconds": 180.961956577, "counter_period_ns": 10000016.377931824, "validated_intervals": 1, "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."}
