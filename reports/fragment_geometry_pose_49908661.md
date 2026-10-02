# Fragment-distance pose precision diagnostic

Frozen failed500update checkpoint,4predeclared control proteins,4noises,6precision/pose variants. No training or model-quality rescue. Original failed control remains failed. Exact double-precision rigid transforms are distinguished from FP32 coordinate-rounding perturbations; saved backbones and every contrast audited.

```json
{
  "status": "complete",
  "original_failure_reproduced": true,
  "exact_rigid_pose_passed": true,
  "small_coordinate_rounding_structurally_stable": true,
  "corrected_precision_profile_qualified": true,
  "records": [
    {
      "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
      "variant": "fp32_rounded_pose",
      "baseline": "fp32_original",
      "latent_max_abs": 1.049041748046875e-05,
      "max_ca_rmsd": 0.00017142909400799558,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
      "variant": "fp64_original",
      "baseline": "fp32_original",
      "latent_max_abs": 9.179115295410156e-06,
      "max_ca_rmsd": 1.2522398255744165e-05,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
      "variant": "fp64_exact_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 8.845955395046393e-15,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
      "variant": "fp64_arbitrary_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 8.845955395046393e-15,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1CB9_1__7ca9cd6d9b60",
      "variant": "fp64_rounded_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 1.239776611328125e-05,
      "max_ca_rmsd": 0.00016954204343543449,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1DGN_1__96f3965253f9",
      "variant": "fp32_rounded_pose",
      "baseline": "fp32_original",
      "latent_max_abs": 0.00020322203636169434,
      "max_ca_rmsd": 0.00029739133301894167,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1DGN_1__96f3965253f9",
      "variant": "fp64_original",
      "baseline": "fp32_original",
      "latent_max_abs": 0.0007082372903823853,
      "max_ca_rmsd": 0.001030782369544267,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1DGN_1__96f3965253f9",
      "variant": "fp64_exact_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.0199203978487174e-14,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1DGN_1__96f3965253f9",
      "variant": "fp64_arbitrary_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.0199203978487174e-14,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "nmr__1DGN_1__96f3965253f9",
      "variant": "fp64_rounded_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0008006691932678223,
      "max_ca_rmsd": 0.0011657224400366847,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "variant": "fp32_rounded_pose",
      "baseline": "fp32_original",
      "latent_max_abs": 1.4826655387878418e-05,
      "max_ca_rmsd": 1.6439640395341553e-05,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "variant": "fp64_original",
      "baseline": "fp32_original",
      "latent_max_abs": 5.538761615753174e-05,
      "max_ca_rmsd": 3.662307823764832e-05,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "variant": "fp64_exact_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 2.636362010715657e-14,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "variant": "fp64_arbitrary_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 2.636362010715657e-14,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P62593__3e6631cbb03c",
      "variant": "fp64_rounded_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 1.5139579772949219e-05,
      "max_ca_rmsd": 1.69442614256889e-05,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "variant": "fp32_rounded_pose",
      "baseline": "fp32_original",
      "latent_max_abs": 7.1302056312561035e-06,
      "max_ca_rmsd": 1.3418634722556497e-05,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "variant": "fp64_original",
      "baseline": "fp32_original",
      "latent_max_abs": 7.510185241699219e-06,
      "max_ca_rmsd": 1.0392452723989997e-05,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "variant": "fp64_exact_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.263852100000829e-14,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "variant": "fp64_arbitrary_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 0.0,
      "max_ca_rmsd": 1.263852100000829e-14,
      "min_ca_lddt": 1.0,
      "same_validity": true
    },
    {
      "target_id": "crypticpocket__P61586__aeabcc544d6c",
      "variant": "fp64_rounded_pose",
      "baseline": "fp64_original",
      "latent_max_abs": 5.602836608886719e-06,
      "max_ca_rmsd": 7.972146181673212e-06,
      "min_ca_lddt": 1.0,
      "same_validity": true
    }
  ],
  "elapsed_seconds": 70.07116408692673,
  "peak_reserved_GiB": 3.841796875,
  "manifest_sha256": "6960703cc4b443f96b7dffc870054623aed2e35547170fc3d0a51d339c08be6d",
  "predictions_sha256": "edb5eb6e8b4ca4698b3a2c2b9c6c203317638f2bb64440f113b8d3e57991944b"
}
```
