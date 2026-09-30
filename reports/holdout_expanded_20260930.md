# Experimental holdout construction

Status: complete.

Selection uses no model scores. Inputs are full polymer sequences with explicit observed-residue maps; at least 90% of CA positions must be observed. Previously used training, benchmark and development chains are excluded.

Training ID coverage audited across 12 caches. Inherited FASTA sequence content is spot-checked, 32 deterministic records per shard; it has not been re-extracted in full.

Recovered candidates: 23542; source rejections: 195.

Locked targets: 34; manifest SHA256: `f711a064d277b412c865566d7a3a8f43f3c8339d1927745f22343e711b3c1ec2`.
Full input lengths 60–426; 32 targets at ≤256 residues and 2 at 257–512. Minimum observed CA fraction 0.901.
Homology exclusions: 23146. MMseqs2 heuristic search at sensitivity 7.5, rejecting ≥30% identity at ≥50% coverage in either direction. One representative per observed connected sequence cluster.
Manifest/source hashes, target/cluster uniqueness, finite coordinates, residue maps and adjacency verified. This is a small operationally independent test relative to the audited exclusion corpus, not a guarantee against remote homology.
Selection computes no model scores. Independent confirmation must use the full polymer inputs and explicit observed-residue maps.
Unknown overlap with pretraining data for frozen ESMC, ProteinAE and the external comparator remains; this is not a claim of independence from pretraining.
