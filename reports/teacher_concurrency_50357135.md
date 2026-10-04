# Concurrent refolding efficiency

```json
{
  "status": "complete",
  "qualified": false,
  "numerical_parity": true,
  "manifest_sha256": "c8c4bf194c12e548ce74d7007b225a20de801f86f963ca19ec82b2288a89fe90",
  "coordinates_sha256": "7ec30a62e1c3f2e38ba7363d0edb3a59f60a4d35384fc308ccd0a7130297bf2c",
  "timed_pair_seconds": {
    "sequential": 64.95838089007884,
    "concurrent": 69.70267153158784
  },
  "seconds_reduction": -0.07303585120967204,
  "buckets": [
    {
      "bucket": 128,
      "seconds": {
        "sequential": 3.5311802071519196,
        "concurrent": 3.170676496811211
      },
      "reduction": 0.10209156406420661
    },
    {
      "bucket": 256,
      "seconds": {
        "sequential": 9.034260772634298,
        "concurrent": 9.70080799749121
      },
      "reduction": -0.07377994078673855
    },
    {
      "bucket": 384,
      "seconds": {
        "sequential": 11.636011626571417,
        "concurrent": 12.499056688975543
      },
      "reduction": -0.07417017876067766
    },
    {
      "bucket": 512,
      "seconds": {
        "sequential": 40.75692828372121,
        "concurrent": 44.332130348309875
      },
      "reduction": -0.08772010588483536
    }
  ],
  "elapsed_seconds": 224.5573779772967,
  "maximum_worker_reserved_gib": 29.63671875,
  "scope": "One assigned GPU, two private models and RNGs, unchangedFP32+fullconfidence,64folds of8archived sequences. Pair walltime includes dispatch and host transfer. Both workers resident in both modes. Pass licenses end-to-end pipeline validation only; not adoption or a scientific accuracy claim."
}
```
