# Paired sampler endpoints

Status: complete.

All sixteen Gaussian seeds and 25-step CFG2 endpoints are retained per protein. These are samples from the inherited student, not new biological-state supervision.

{
  "status": "complete",
  "pairs": 2048,
  "proteins": 128,
  "controls": [
    {
      "bucket": 512,
      "latent_rmse": 8.40584107208997e-07,
      "ca_rmsd": 5.9006918124316486e-05,
      "tm_after_kabsch": 0.9999999999455387,
      "ca_lddt": 1.0
    },
    {
      "bucket": 384,
      "latent_rmse": 8.110256999316334e-07,
      "ca_rmsd": 2.360620909307406e-05,
      "tm_after_kabsch": 0.999999999988748,
      "ca_lddt": 1.0
    },
    {
      "bucket": 256,
      "latent_rmse": 3.63754384125059e-06,
      "ca_rmsd": 9.535524559015788e-05,
      "tm_after_kabsch": 0.9999999997252819,
      "ca_lddt": 1.0
    },
    {
      "bucket": 128,
      "latent_rmse": 8.316253570228582e-07,
      "ca_rmsd": 2.1874174327257485e-05,
      "tm_after_kabsch": 0.9999999999728091,
      "ca_lddt": 1.0
    }
  ],
  "seconds": 531.1139628830133,
  "peak_reserved_gib": 15.0390625
}
