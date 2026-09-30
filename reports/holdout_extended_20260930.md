# Experimental holdout construction

Status: failed.

Selection uses no model scores. Inputs are full polymer sequences with explicit observed-residue maps; at least 90% of CA positions must be observed. Previously used training, benchmark and development chains are excluded.

Training ID coverage audited across 12 caches. Inherited FASTA sequence content is spot-checked, 32 deterministic records per shard; it has not been re-extracted in full.

Recovered candidates: 8235; source rejections: 82.

Failure: ValueError: only 11 independent, mapped recent structures; holdout not locked. No final test has been locked.
