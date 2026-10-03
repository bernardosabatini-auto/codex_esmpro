# Codec batching diagnosis

The padded batch16profile50121087failed its unchanged numerical gates. Encoder differences reached0.00854; the30fragment cases needing no padding differed by at most1.1e-6and their decoderCA RMSD stayed below1.1e-5Å. This pointed to padding, not an intrinsic inability to batch.

Exact-length batch16profile50121944passed all644historical/full-chain/fragment parity controls and preserved all prior qualification decisions, including failures. All192additive20-residue crops passed properCA RMSD anddRMS≤0.5Å. Peak reserved memory was2.16GiB; batched codec calls took6.73swithin39.01sworker time. The workload includes additional short crops, so an unadjusted speedup against the older pilot would be misleading. The padded failure remains archived and no tolerance was relaxed.
