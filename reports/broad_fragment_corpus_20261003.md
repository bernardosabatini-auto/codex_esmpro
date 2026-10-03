# Source-verified fragment training expansion

All four one-RTX construction jobs passed independent CPU audits: 50124939, 50124993, 50125034, 50125073.

- 7429/7680 new source-backed proteins passed the fixed full-endpoint screen; 251 rejections remain in the ledger, without replacements.
- Retaining all original512 gives **7941 training proteins**. All original nine training conditions and16 development inputs are preserved exactly.
- Fractional isolated-crop roundtrips: 66653/69120 satisfy both proper CA RMSD and distance RMSD<=0.5A.
- Additive20-residue crop roundtrips: 24547/24576 satisfy both limits. Every crop, including failures, remains on each retained protein.
- All64 historical, singleton-batch and rigid-pose controls passed. Qualified exact-length batching avoids the previously rejected padding effect.

Next is a predeclared four-arm continuation from the same6000-update checkpoint:512 versus7941 proteins, each with weight3 versus equal motif/scaffold loss mass. Both corpora add the same short-condition recipe. Each arm first gets a40-update profile. No new teacher labels were generated; broader data uses verified AFDB structures, not experimental ground truth. Corpus and source-distribution changes prevent interpreting this as a pure scaling law.

The evaluation remains strict motif retention and global/scaffold agreement in the same valid refold, with fixed ProteinMPNN/refolding budgets. Raw retention or geometry alone does not demonstrate designability.
