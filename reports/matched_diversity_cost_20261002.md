# Matched development diversity and inference cost

Descriptive analysis of the four state-eligible families in the fixed eight-sequence RTX timing panel. These are a small selected development subset, not a new validation set. The same frozen contact definitions,2A/0.8/coarse-valid gate and every original sample are retained. K8 is rescored from stored predictions; K1/4/16/32 must exactly reproduce the existing scores.

| Pipeline | K | Mean seconds | Mean valid state coverage |
|---|---:|---:|---:|
| original | 1 | 0.7962 | 0.2500 |
| original | 8 | 2.9250 | 0.2500 |
| original | 32 | 10.5144 | 0.2500 |
| candidate | 1 | 0.5108 | 0.1250 |
| candidate | 8 | 1.5397 | 0.2500 |
| candidate | 32 | 5.2354 | 0.3750 |
| teacher | 1 | 2.4533 | 0.1250 |
| teacher | 8 | 3.1394 | 0.3750 |
| teacher | 32 | 5.8009 | 0.5000 |

Budget estimates choose the largest measured K in{1,8,32} fitting each family’s latency median, using latency alone. No sample means zero coverage. No interpolation, extrapolation, sample selection or restart policy. These combine stored ensemble prefixes with separately measured runtime distributions; teacher timing uses different random seeds. They are estimates, not timed deadline-enforced experiments. Loading/warmup and confidence heads are outside the measured scope.

| Seconds per family | Original | Compact balanced500 | Teacher |
|---|---:|---:|---:|
| 0.5 | 0.0000 | 0.0000 | 0.0000 |
| 1 | 0.2500 | 0.1250 | 0.1250 |
| 2 | 0.2500 | 0.3750 | 0.2500 |
| 4 | 0.2500 | 0.3750 | 0.3750 |
| 8 | 0.2500 | 0.3750 | 0.3750 |
| 16 | 0.2500 | 0.3750 | 0.5000 |

The JSON retains every per-family count, coverage, latency and paired-family interval. Four families and fixed random prefixes do not support a broad performance verdict; this analysis does not qualify a model or change any gate. Do not mix these matched curves with the16-family overall coverage means.
