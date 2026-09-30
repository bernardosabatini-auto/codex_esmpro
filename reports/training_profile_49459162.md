# Backward profile

Status: complete

Profile draws are all conditioned, late time, and self-conditioned; capacity stress rather than representative training. Adam state and optimizer arithmetic are included; learning rate zero preserves checkpoint weights.

| Length | Arm | Batch | Proteins/s | Reserved GiB |
|---:|---|---:|---:|---:|
| 128 | flow | 128 | 68.97 | 39.65 |
| 128 | geometry | 128 | 40.08 | 46.36 |
| 256 | flow | 64 | 18.98 | 71.86 |
| 256 | geometry | 64 | 11.03 | 84.17 |
| 384 | flow | 32 | 8.55 | 80.38 |
| 384 | geometry | 32 | 4.93 | 94.62 |
| 512 | flow | 16 | 4.57 | 70.63 |
| 512 | geometry | 16 | 2.59 | 85.92 |

Candidate full-parameter gradient controls: [{"length": 90, "padded_length": 128, "fp32_loss": 0.057252801954746246, "candidate_loss": 0.057284947484731674, "candidate_precision": "fp16", "gradient_cosine": 0.9998652480914523, "relative_l2": 0.016426251200022154, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 0.047935206912877455}, {"length": 170, "padded_length": 256, "fp32_loss": 0.023393604904413223, "candidate_loss": 0.023379957303404808, "candidate_precision": "fp16", "gradient_cosine": 0.9998461270674954, "relative_l2": 0.017715125834457793, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 0.07532723178669369}, {"length": 340, "padded_length": 384, "fp32_loss": 0.04728097468614578, "candidate_loss": 0.047262512147426605, "candidate_precision": "fp16", "gradient_cosine": 0.9999342357341446, "relative_l2": 0.011516289062539401, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 2.129915110478947}, {"length": 394, "padded_length": 512, "fp32_loss": 0.05720685422420502, "candidate_loss": 0.05724532529711723, "candidate_precision": "fp16", "gradient_cosine": 0.999894022461, "relative_l2": 0.014604841743407319, "passed": true, "weighted_aux_to_flow_parameter_grad_ratio": 0.0722438678413258}]

Hardware: {"whole_capture_mean_percent": {"SMs Active [Throughput %]": 63.49583568163317, "SM Issue [Throughput %]": 27.257311040140273, "Tensor Active [Throughput %]": 4.136514496837623, "DRAM Read Bandwidth [Throughput %]": 15.474043459202205, "DRAM Write Bandwidth [Throughput %]": 9.526269647441918}, "collection_mean_percent": {"SMs Active [Throughput %]": 90.12141143009511, "SM Issue [Throughput %]": 38.68705003999644, "Tensor Active [Throughput %]": 5.871122566882944, "DRAM Read Bandwidth [Throughput %]": 21.944004977335346, "DRAM Write Bandwidth [Throughput %]": 13.210914585370189}, "capture_seconds": 159.679727186, "collection_seconds": 112.511729521, "counter_period_ns": 9999982.91495491, "validated_intervals": 1, "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."}
