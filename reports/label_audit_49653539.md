# Full teacher-latent reconstruction audit

Status: complete; training gate passed: True.

All8,192 teacher conformations across512 training families, three ProteinAE decoder steps, fixed decoder noise within each protein. GPU metrics checked against CPU references in all four length buckets. Thresholds: mean CA lDDT at least0.98, decoded coarse validity no more than0.01 below input validity.

mean_ca_lddt: 0.9994075821014121

min_ca_lddt: 0.935356080532074

mean_ca_rmsd: 0.1953426469117403

input_valid_fraction: 0.9957275390625

decoded_valid_fraction: 0.991455078125
