# Local backbone closure

```json
{
  "status": "complete",
  "profile_only": false,
  "numerically_qualified": true,
  "qualified": false,
  "manifest_path": "/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/local_closure_canonical_full_20261004/manifest.json",
  "manifest_sha256": "70aad6db06afa52fc78f77667786cd15c38ca2442f92c28ca5c8cbc7b82f22a3",
  "predictions_sha256": "400c7f3cd48a96d42c822f7ec41181cfe7548a83d1cb38bf6a689854440005e4",
  "protocol_sha256": "56b64d5f3be6cb33526ac2e2491652396be06f4bfb3df9b0b7a1adda8681a470",
  "elapsed_seconds": 232.95005450793542,
  "estimated_full_seconds": 457,
  "controls": 20,
  "prefix_max_abs": 0.0,
  "summary": [
    {
      "arm": "generated_cond",
      "samples": 128,
      "coarse_valid": 91,
      "connected_raw": 89,
      "qualified_raw": 30,
      "local_geometry": 32,
      "mean_max_atom_displacement": 5.950464593246579
    },
    {
      "arm": "generated_untrained",
      "samples": 128,
      "coarse_valid": 69,
      "connected_raw": 67,
      "qualified_raw": 18,
      "local_geometry": 29,
      "mean_max_atom_displacement": 8.103516474366188
    },
    {
      "arm": "native_cond",
      "samples": 128,
      "coarse_valid": 115,
      "connected_raw": 115,
      "qualified_raw": 115,
      "local_geometry": 128,
      "mean_max_atom_displacement": 0.8606997863389552
    }
  ],
  "scope": "CPU-only local closure; fixed motif and far scaffold, generated-parent geometry targets. Native arm explicitly oracle. All failures retained. Geometric feasibility alone does not establish designability or same-refold motif/global/scaffold agreement."
}
```


The fixed recipe fails its45/128advancement floor:30generated complete geometry passes,
versus18untrained and115native-context. The identical full gate gives0passes in all
three arms before closure. Trained minus untrained afterclosure is9.375percentagepoints,
family-bootstrap95%interval3.906to15.625points; this remains a repeated training-only
geometry result, not designability.

Necessary fixed-anchor reachability bounds rule out27generated and28untrained local
bridges; none of the native bridges is excluded. These are conservative impossibility
bounds under the declared0.05A/10degree tolerances. They do not settle the other failures.
No duration/window/strength sweep or GPUrefolding follows this failed recipe.

The next prospective diagnostic supplies each frozen decoder its own compatible
parent-derived isolated fragment. It distinguishes conflict with the requested motif
from failure on generated latent contexts; it is explicitly not a scaffolding success test.
