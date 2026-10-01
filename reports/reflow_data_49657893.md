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
      "latent_rmse": 1.4198762073647231e-05,
      "ca_rmsd": 0.00042246289608247165,
      "tm_after_kabsch": 0.9999999972267174,
      "ca_lddt": 1.0
    },
    {
      "bucket": 384,
      "latent_rmse": 2.5046551854757126e-06,
      "ca_rmsd": 5.726358852423055e-05,
      "tm_after_kabsch": 0.9999999999339413,
      "ca_lddt": 1.0
    },
    {
      "bucket": 256,
      "latent_rmse": 9.253263328901085e-07,
      "ca_rmsd": 1.7118866851600437e-05,
      "tm_after_kabsch": 0.9999999999915677,
      "ca_lddt": 1.0
    },
    {
      "bucket": 128,
      "latent_rmse": 7.167509465944022e-07,
      "ca_rmsd": 1.2876557655124704e-05,
      "tm_after_kabsch": 0.9999999999904159,
      "ca_lddt": 1.0
    }
  ],
  "seconds": 532.246188681107,
  "peak_reserved_gib": 15.25390625
}
