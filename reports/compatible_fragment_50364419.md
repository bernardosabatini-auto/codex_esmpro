# Frozen compatible-fragment diagnostic

```json
{
  "status": "complete",
  "diagnostic_only": true,
  "numerically_qualified": true,
  "manifest_sha256": "3ca859fa5d233a1d07aa8551f2e96e00df0b184a8c1250faf9183cc84e49dc39",
  "predictions_sha256": "e89f6ecf62b4d05c0c7b485cf5b421f170e81b9ce7f330108435a1d63b5ba578",
  "closed_sha256": "e3291b892dd57ba2dbd67bad951fe1d99a05e3a3eb67a571afcbed75b0ac727d",
  "closure_manifest_sha256": "89ad74c2f24c17893882c6169005ffa378e4298da5ba99e45443018da24f1258",
  "controls": 80,
  "summary": [
    {
      "arm": "trained_generated_compatible",
      "samples": 128,
      "raw_coarse": 126,
      "raw_connected": 11,
      "raw_complete": 0,
      "closed_coarse": 127,
      "closed_connected": 127,
      "closed_complete": 127
    },
    {
      "arm": "untrained_generated_compatible",
      "samples": 128,
      "raw_coarse": 80,
      "raw_connected": 0,
      "raw_complete": 0,
      "closed_coarse": 92,
      "closed_connected": 92,
      "closed_complete": 88
    },
    {
      "arm": "trained_native_compatible",
      "samples": 128,
      "raw_coarse": 113,
      "raw_connected": 14,
      "raw_complete": 0,
      "closed_coarse": 115,
      "closed_connected": 115,
      "closed_complete": 115
    },
    {
      "arm": "untrained_native_compatible",
      "samples": 128,
      "raw_coarse": 57,
      "raw_connected": 0,
      "raw_complete": 0,
      "closed_coarse": 90,
      "closed_connected": 89,
      "closed_complete": 82
    }
  ],
  "contrasts": [
    {
      "arm": "trained_generated_compatible",
      "original_desired_arm": "generated_cond",
      "closed_complete_difference": {
        "mean": 0.7578125,
        "ci95": [
          0.671875,
          0.8359375
        ],
        "families": 32
      }
    },
    {
      "arm": "untrained_generated_compatible",
      "original_desired_arm": "generated_untrained",
      "closed_complete_difference": {
        "mean": 0.546875,
        "ci95": [
          0.421875,
          0.671875
        ],
        "families": 32
      }
    },
    {
      "arm": "trained_native_compatible",
      "original_desired_arm": "native_cond",
      "closed_complete_difference": {
        "mean": 0.0,
        "ci95": [
          0.0,
          0.0
        ],
        "families": 32
      }
    }
  ],
  "next_route": "global_scaffold_remodeling",
  "gpu_elapsed_seconds": 58.439505802001804,
  "peak_reserved_GiB": 5.705078125,
  "cpu_closure_seconds": 281.8595464406535,
  "scope": "Artificial compatible-fragment diagnostic,32training proteins andfour original noises. Replacing the desired motif with model-own geometry cannot demonstrate scaffolding or designability. Same frozen decoder/context/noise; only isolated condition changed. Original desired-fragment failures remain closed. No refolding licensed."
}
```


Interpretation: the trained decoder plus unchanged local closure can handle generated
contexts when their own compatible motif is supplied:127/128complete geometry passes,
versus30/128with the requested motif. The paired difference is75.78percentagepoints
(32family bootstrap95%interval67.19–83.59). Native compatible and original-desired
conditions have identical115/128complete outcomes. This points toward conflicting
scaffold context as the dominant failure here, not a general inability to decode
generated latents. Raw junction geometry still requires correction: only11/128trained
generated compatible samples pass the connected raw gate before closure.

These are artificial compatibility controls, not scaffolding or designability successes.
No refolds are launched for them. Next is the original desired-fragment task with
three frozen whole-context encode/decode updates, specified in
`configs/fragment_context_refresh_protocol.json`; all scaffold positions can respond.
