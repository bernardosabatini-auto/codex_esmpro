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
      "latent_rmse": 1.8084894009007257e-06,
      "ca_rmsd": 5.064167888537236e-05,
      "tm_after_kabsch": 0.9999999999600839,
      "ca_lddt": 1.0
    },
    {
      "bucket": 384,
      "latent_rmse": 4.977756179869175e-05,
      "ca_rmsd": 0.00026343988322904537,
      "tm_after_kabsch": 0.9999999986178162,
      "ca_lddt": 1.0
    },
    {
      "bucket": 256,
      "latent_rmse": 1.2892069207737222e-06,
      "ca_rmsd": 2.9351097460372794e-05,
      "tm_after_kabsch": 0.9999999999753906,
      "ca_lddt": 1.0
    },
    {
      "bucket": 128,
      "latent_rmse": 7.485632522730157e-07,
      "ca_rmsd": 1.1197627717183589e-05,
      "tm_after_kabsch": 0.9999999999927522,
      "ca_lddt": 1.0
    }
  ],
  "seconds": 530.6283306325786,
  "peak_reserved_gib": 15.197265625
}
