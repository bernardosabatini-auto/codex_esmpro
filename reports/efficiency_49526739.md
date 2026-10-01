# Activation recomputation profile

FP16 head, fixed scale 128, always self-conditioned capacity stress. Real Adam and EMA storage/arithmetic. Repeated profile inputs are not independent proteins.

Status: failed

| Padded length | Policy | Batch | Proteins/s | Reserved GiB | SM issue % |
|---:|---|---:|---:|---:|---:|

ValueError: recomputation gradient equivalence failed

Only compare unchanged batch sizes for direct adoption into matched training. Half-batch measurements are capacity diagnostics. Recheck actual training trajectory before using any faster policy for new scientific comparisons. SM issue is not percent of peak FLOPs.

```json
[
  {
    "length": 128,
    "relative_gradient_l2": 0.0010019276115630616,
    "loss_change": 0.0,
    "passed": false
  }
]
```
