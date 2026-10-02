# Fragment handedness diagnostic

Reflection-allowed fits diagnose an ambiguity of distance inputs; they never qualify a scaffold. All development samples retained.

```json
{
  "status": "complete",
  "interpretation": "Diagnostic only. Reflection-allowed fitting is never a success criterion; threshold and designability requirements unchanged.",
  "sources": [
    {
      "run": "runs/fragment_guidance_49927209",
      "manifest_sha256": "b2484153198af59a74f563348beafd5ccf7148a60095696e3d3c92a6f14cc2d2",
      "predictions_sha256": "d3e988339763cf6276f0eff1b5fe8b05fcfbe4bdc40e5f049bace37b59f3769a"
    },
    {
      "run": "runs/fragment_training_49893014",
      "manifest_sha256": "3fbef1865392329c3688f43a8dff2a0312f5289716568f9f8d8ca8a9d8647d61",
      "predictions_sha256": "8998fffbecc12d6f09577eda10d58beacf2c8d0be353ab0c3a30f997aae54275"
    },
    {
      "run": "runs/fragment_training_49893256",
      "manifest_sha256": "755d309ff80bf2eee45e57419bca8c63cc9033ac60a5d0217a7ab8009fee086d",
      "predictions_sha256": "3cb8bc2615f7a93f11826d0f7a9478a24126e2ca16504cf779e5f76f86017d2e"
    }
  ],
  "summaries": [
    {
      "run": "fragment_guidance_49927209",
      "group": "guidance1",
      "samples": 64,
      "reflection_preferred": 20,
      "reflection_gain_over_1A": 10,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 5.373419814391983,
      "mean_unrestricted_rmsd": 4.757298152094387
    },
    {
      "run": "fragment_guidance_49927209",
      "group": "guidance2",
      "samples": 64,
      "reflection_preferred": 16,
      "reflection_gain_over_1A": 7,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 4.268228023213281,
      "mean_unrestricted_rmsd": 3.671626753448793
    },
    {
      "run": "fragment_training_49893014",
      "group": "development/conditioned",
      "samples": 64,
      "reflection_preferred": 27,
      "reflection_gain_over_1A": 7,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 8.946562971424221,
      "mean_unrestricted_rmsd": 8.602361884091849
    },
    {
      "run": "fragment_training_49893256",
      "group": "development/conditioned",
      "samples": 64,
      "reflection_preferred": 19,
      "reflection_gain_over_1A": 10,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 8.23346873353237,
      "mean_unrestricted_rmsd": 7.853485705422418
    }
  ],
  "records": "See ignored raw JSON"
}
```
