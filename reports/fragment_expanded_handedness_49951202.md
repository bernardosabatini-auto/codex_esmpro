# Fragment handedness diagnostic

Reflection-allowed fits diagnose an ambiguity of distance inputs; they never qualify a scaffold. All development samples retained.

```json
{
  "status": "complete",
  "interpretation": "Diagnostic only. Reflection-allowed fitting is never a success criterion; threshold and designability requirements unchanged.",
  "sources": [
    {
      "run": "runs/fragment_training_49929751",
      "manifest_sha256": "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
      "predictions_sha256": "714bf76ba30e37a2a9bd5474684784678eafd72488efacd3e87574a233c940a5"
    },
    {
      "run": "runs/fragment_training_49939857",
      "manifest_sha256": "d3ea388805b4e0d17ae5ea2c687fd71012026399581221a485abab66be072423",
      "predictions_sha256": "2239a8ad1ea53c9de81d9fc0aad706a0cdddf08108938ed294cf5c4815f34f2d"
    },
    {
      "run": "runs/fragment_training_49951202",
      "manifest_sha256": "d77f4dc0f619f7cc905d440e9d5da7ea57c362b6902a2309532c93b6eac3d623",
      "predictions_sha256": "ad23c4e7fe0a449369fdcb0562b2bf96a57bd92f5ff075e33ab87632fc1d3a93"
    }
  ],
  "summaries": [
    {
      "run": "fragment_training_49929751",
      "group": "development/conditioned",
      "samples": 64,
      "reflection_preferred": 21,
      "reflection_gain_over_1A": 9,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 4.867760111507188,
      "mean_unrestricted_rmsd": 4.210380692495307
    },
    {
      "run": "fragment_training_49939857",
      "group": "development/conditioned",
      "samples": 64,
      "reflection_preferred": 20,
      "reflection_gain_over_1A": 10,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 5.368506846232206,
      "mean_unrestricted_rmsd": 4.821830418026247
    },
    {
      "run": "fragment_training_49951202",
      "group": "development/conditioned",
      "samples": 64,
      "reflection_preferred": 9,
      "reflection_gain_over_1A": 6,
      "reflection_only_below_1A": 0,
      "mean_proper_rmsd": 3.3832445861056253,
      "mean_unrestricted_rmsd": 2.9480466680413353
    }
  ],
  "records": "See ignored raw JSON"
}
```
