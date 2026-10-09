# Context-code scaffold generation

The unprojected contextual-code recipe failed: both learned arms had only 2/128
coarse-valid structures and zero original-motif matches. All 256 samples remain
reported; no ProteinMPNN/refolding was launched. Sixteen historical oracle
replays passed, isolating the failure from changes to the scaffold sampler.

A subsequent CPU audit found that the new context-code sampler omitted the
per-residue terminal normalization used by the inherited latent pipeline. Native
labels have mean zero and norm sqrt(8) per residue. Sampled isolated codes had
residue standard deviation 0.863–1.077 and maximum absolute residue mean 0.03483.
Projection changes them by RMS 0.02395. This was an implementation oversight;
it is not yet an explanation for the structural failure. Adjacent-code distances
also have heavier tails than native targets, which normalization may not repair.
A separate prospectively bounded four-family correction diagnostic is specified
in configs/context_normalization_profile_protocol.json. Original results, code,
and thresholds remain preserved; no training or duration extension.

The single RTX allocation lasted 284 seconds (0.0789 GPU-hours), peak reserved
memory 6.82 GiB. Assigned-UUID capture gave 82.65% SM activity and 42.59% weighted
utilization over 223 seconds, excluding startup. Both arms shared loaded frozen
weights in one allocation. Final scientific audits ran on CPU after GPU release.

```json
{
  "status": "complete",
  "manifest_sha256": "d4fd3dab483087c02fab2caf8624b39fb2869ce34768f7def017f9531d86f661",
  "predictions_sha256": "89917141beee8e8f5bc1c289437f1d9ea757c11922993b9f91863e626c4fa443",
  "summary": {
    "isolated": {
      "raw": 0,
      "valid": 2,
      "qualified": false,
      "mean_motif_rmsd": 5.964341715867825
    },
    "ablated": {
      "raw": 0,
      "valid": 2,
      "qualified": false,
      "mean_motif_rmsd": 6.413756468912041
    },
    "parent": {
      "raw": 25,
      "valid": 128,
      "qualified": true,
      "mean_motif_rmsd": 2.251629539928018
    }
  },
  "controls": 4,
  "control_samples": 16,
  "designability_tested": false,
  "generation_seconds": 207.03650738392025,
  "elapsed_seconds": 273.2982785780914,
  "peak_reserved_GiB": 6.818359375
}
```
