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
      "latent_rmse": 2.615807488837163e-06,
      "ca_rmsd": 7.14782088037636e-05,
      "tm_after_kabsch": 0.9999999999206103,
      "ca_lddt": 1.0
    },
    {
      "bucket": 384,
      "latent_rmse": 3.7107129173818976e-06,
      "ca_rmsd": 7.223061433702383e-05,
      "tm_after_kabsch": 0.9999999998960929,
      "ca_lddt": 1.0
    },
    {
      "bucket": 256,
      "latent_rmse": 9.010716439661337e-07,
      "ca_rmsd": 2.3315298576868327e-05,
      "tm_after_kabsch": 0.999999999983702,
      "ca_lddt": 1.0
    },
    {
      "bucket": 128,
      "latent_rmse": 6.832868848505314e-07,
      "ca_rmsd": 1.1545893949199728e-05,
      "tm_after_kabsch": 0.9999999999923601,
      "ca_lddt": 1.0
    }
  ],
  "seconds": 535.3900880212896,
  "peak_reserved_gib": 15.25390625
}
