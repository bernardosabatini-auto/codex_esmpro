# ProteinAE latent pose diagnostic

Status: complete.

Sixteen training structures, eight proper rotations and translations. These inputs describe the same conformation. Canonical coordinates use the first residue N/CA/C frame. Decoder noise is fixed across rotations.

| Encoder input | Latent RMSE across poses | Decoded CA RMSD to source (A) |
|---|---:|---:|
| raw | 0.989270 | 0.3361 |
| canonical | 0.000002 | 0.3516 |
