# AdamW implementation profile

Status: complete. All-block recomputation and scientific batch sizes are retained.

| Length | AdamW | Batch | Proteins/s | Reserved GiB | SM issue % |
|---:|---|---:|---:|---:|---:|
| 128 | single_tensor_adamw | 128 | 69.72 | 41.7 | 42.6 |
| 128 | fused_adamw | 128 | 70.28 | 41.7 | 42.9 |
| 256 | single_tensor_adamw | 64 | 19.06 | 74.1 | 42.9 |
| 256 | fused_adamw | 64 | 19.15 | 74.1 | 43.0 |
| 384 | single_tensor_adamw | 32 | 8.59 | 82.1 | 42.5 |
| 384 | fused_adamw | 32 | 8.62 | 82.1 | 42.7 |
| 512 | single_tensor_adamw | 16 | 4.59 | 72.6 | 40.1 |
| 512 | fused_adamw | 16 | 4.61 | 72.6 | 40.2 |

Optimizer arithmetic controls do not establish training-trajectory equivalence. Any adoption requires an actual matched trajectory test. SM issue is not percent of peak FLOPs.

```json
{
  "status": "complete",
  "rows": [
    {
      "length": 128,
      "batch": 128,
      "policy": "single_tensor_adamw",
      "status": "complete",
      "seconds": 1.8357967957272194,
      "proteins_per_second": 69.72449254618891,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::128::single_tensor_adamw::128::0"
        },
        {
          "nvtx_range": "optimizer_profile::128::single_tensor_adamw::128::1"
        },
        {
          "nvtx_range": "optimizer_profile::128::single_tensor_adamw::128::2"
        },
        {
          "nvtx_range": "optimizer_profile::128::single_tensor_adamw::128::3"
        }
      ],
      "peak_reserved_bytes": 44728057856,
      "peak_allocated_bytes": 41512431104,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 95.50068027210884,
          "SM Issue [Throughput %]": 42.57142857142857,
          "Tensor Active [Throughput %]": 7.095238095238095,
          "DRAM Read Bandwidth [Throughput %]": 25.080272108843538,
          "DRAM Write Bandwidth [Throughput %]": 14.774149659863946
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 7.343289886,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 128,
      "batch": 128,
      "policy": "fused_adamw",
      "status": "complete",
      "seconds": 1.8213933849474415,
      "proteins_per_second": 70.27586739791174,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::128::fused_adamw::128::0"
        },
        {
          "nvtx_range": "optimizer_profile::128::fused_adamw::128::1"
        },
        {
          "nvtx_range": "optimizer_profile::128::fused_adamw::128::2"
        },
        {
          "nvtx_range": "optimizer_profile::128::fused_adamw::128::3"
        }
      ],
      "peak_reserved_bytes": 44728057856,
      "peak_allocated_bytes": 41512671232,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 96.15775034293553,
          "SM Issue [Throughput %]": 42.945130315500684,
          "Tensor Active [Throughput %]": 7.1508916323731135,
          "DRAM Read Bandwidth [Throughput %]": 25.29766803840878,
          "DRAM Write Bandwidth [Throughput %]": 14.821673525377228
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 7.28565569,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 256,
      "batch": 64,
      "policy": "single_tensor_adamw",
      "status": "complete",
      "seconds": 3.3575928786885925,
      "proteins_per_second": 19.061274642980866,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::256::single_tensor_adamw::64::0"
        },
        {
          "nvtx_range": "optimizer_profile::256::single_tensor_adamw::64::1"
        },
        {
          "nvtx_range": "optimizer_profile::256::single_tensor_adamw::64::2"
        },
        {
          "nvtx_range": "optimizer_profile::256::single_tensor_adamw::64::3"
        }
      ],
      "peak_reserved_bytes": 79582724096,
      "peak_allocated_bytes": 73276288512,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 97.58227848101266,
          "SM Issue [Throughput %]": 42.85107967237528,
          "Tensor Active [Throughput %]": 6.668652271034996,
          "DRAM Read Bandwidth [Throughput %]": 22.084884586746092,
          "DRAM Write Bandwidth [Throughput %]": 14.886820551005211
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 13.430457907,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 256,
      "batch": 64,
      "policy": "fused_adamw",
      "status": "complete",
      "seconds": 3.3428115975111723,
      "proteins_per_second": 19.145559997353725,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::256::fused_adamw::64::0"
        },
        {
          "nvtx_range": "optimizer_profile::256::fused_adamw::64::1"
        },
        {
          "nvtx_range": "optimizer_profile::256::fused_adamw::64::2"
        },
        {
          "nvtx_range": "optimizer_profile::256::fused_adamw::64::3"
        }
      ],
      "peak_reserved_bytes": 79584821248,
      "peak_allocated_bytes": 73276528640,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 97.89827973074047,
          "SM Issue [Throughput %]": 43.03739715781601,
          "Tensor Active [Throughput %]": 6.68661181750187,
          "DRAM Read Bandwidth [Throughput %]": 22.148840688107704,
          "DRAM Write Bandwidth [Throughput %]": 14.923709798055349
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 13.371323107,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 384,
      "batch": 32,
      "policy": "single_tensor_adamw",
      "status": "complete",
      "seconds": 3.726939288841095,
      "proteins_per_second": 8.58613396140148,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::384::single_tensor_adamw::32::0"
        },
        {
          "nvtx_range": "optimizer_profile::384::single_tensor_adamw::32::1"
        },
        {
          "nvtx_range": "optimizer_profile::384::single_tensor_adamw::32::2"
        },
        {
          "nvtx_range": "optimizer_profile::384::single_tensor_adamw::32::3"
        }
      ],
      "peak_reserved_bytes": 88116035584,
      "peak_allocated_bytes": 81133702656,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 97.68544600938966,
          "SM Issue [Throughput %]": 42.48356807511737,
          "Tensor Active [Throughput %]": 6.463447350771294,
          "DRAM Read Bandwidth [Throughput %]": 21.93963782696177,
          "DRAM Write Bandwidth [Throughput %]": 14.7719651240778
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 14.907845945,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 384,
      "batch": 32,
      "policy": "fused_adamw",
      "status": "complete",
      "seconds": 3.712724598008208,
      "proteins_per_second": 8.619007188727995,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::384::fused_adamw::32::0"
        },
        {
          "nvtx_range": "optimizer_profile::384::fused_adamw::32::1"
        },
        {
          "nvtx_range": "optimizer_profile::384::fused_adamw::32::2"
        },
        {
          "nvtx_range": "optimizer_profile::384::fused_adamw::32::3"
        }
      ],
      "peak_reserved_bytes": 88116035584,
      "peak_allocated_bytes": 81133942784,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 97.92794612794613,
          "SM Issue [Throughput %]": 42.66936026936027,
          "Tensor Active [Throughput %]": 6.492255892255892,
          "DRAM Read Bandwidth [Throughput %]": 21.98181818181818,
          "DRAM Write Bandwidth [Throughput %]": 14.795286195286195
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 14.850979821,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 512,
      "batch": 16,
      "policy": "single_tensor_adamw",
      "status": "complete",
      "seconds": 3.4846305653918535,
      "proteins_per_second": 4.591591475695148,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::512::single_tensor_adamw::16::0"
        },
        {
          "nvtx_range": "optimizer_profile::512::single_tensor_adamw::16::1"
        },
        {
          "nvtx_range": "optimizer_profile::512::single_tensor_adamw::16::2"
        },
        {
          "nvtx_range": "optimizer_profile::512::single_tensor_adamw::16::3"
        }
      ],
      "peak_reserved_bytes": 77944848384,
      "peak_allocated_bytes": 73109646848,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 97.65900933237617,
          "SM Issue [Throughput %]": 40.054558506819816,
          "Tensor Active [Throughput %]": 6.155061019382628,
          "DRAM Read Bandwidth [Throughput %]": 25.582196697774588,
          "DRAM Write Bandwidth [Throughput %]": 13.803302225412779
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 13.938604065,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    },
    {
      "length": 512,
      "batch": 16,
      "policy": "fused_adamw",
      "status": "complete",
      "seconds": 3.4709602660732344,
      "proteins_per_second": 4.60967535595016,
      "batches": [
        {
          "nvtx_range": "optimizer_profile::512::fused_adamw::16::0"
        },
        {
          "nvtx_range": "optimizer_profile::512::fused_adamw::16::1"
        },
        {
          "nvtx_range": "optimizer_profile::512::fused_adamw::16::2"
        },
        {
          "nvtx_range": "optimizer_profile::512::fused_adamw::16::3"
        }
      ],
      "peak_reserved_bytes": 77944848384,
      "peak_allocated_bytes": 73109886976,
      "hardware": {
        "whole_capture_mean_percent": {
          "SMs Active [Throughput %]": 46.90812007300687,
          "SM Issue [Throughput %]": 20.213467438157743,
          "Tensor Active [Throughput %]": 3.148033086093744,
          "DRAM Read Bandwidth [Throughput %]": 11.43994407984156,
          "DRAM Write Bandwidth [Throughput %]": 7.434546231214322
        },
        "collection_mean_percent": {
          "SMs Active [Throughput %]": 97.91360691144709,
          "SM Issue [Throughput %]": 40.22174226061915,
          "Tensor Active [Throughput %]": 6.174946004319654,
          "DRAM Read Bandwidth [Throughput %]": 25.645788336933045,
          "DRAM Write Bandwidth [Throughput %]": 13.840892728581714
        },
        "capture_seconds": 257.500161959,
        "collection_seconds": 13.883920006,
        "counter_period_ns": 10000006.289669903,
        "validated_intervals": 4,
        "caveat": "SM activity includes waiting warps; it is not FLOP efficiency. Whole capture excludes profiler export after collection."
      }
    }
  ],
  "controls": [
    {
      "relative_update_l2": 0.00023898985730889813,
      "max_parameter_difference": 9.5367431640625e-07,
      "passed": true,
      "scope": "Four optimizer updates with identical real clipped gradients and initial weights. This checks optimizer arithmetic, not a training trajectory."
    }
  ],
  "scope": "FP16 head with fixed scale 128, original all-block activation recomputation, always self-conditioned stress. Compare single-tensor versus fused AdamW; no trained checkpoint saved.",
  "seconds": 222.56901788595133
}
```
