# Isolated-fragment generation: current evidence

The model is explicitly conditioned on an isolated fragment, its supplied sequence, and placement. Scaffold sequence and native scaffold coordinates are excluded from conditioning.

## What counts as success

The generated backbone must be valid and retain the fragment. One of eight designed-sequence refolds must itself be valid, retain the fragment, and agree globally with the generated backbone. The stronger supplement also requires scaffold-only TM > 0.5 in that **same refold**. Sequence attempts cannot be pooled across experiments. Geometry alone is insufficient.

## Established results

- The weighted 6,000-update model produced one strict success among 64 fixed-noise development samples; that success also passes scaffold agreement.
- Fresh-noise testing gives one scaffold-qualified success among 64 whole-panel samples for both weighted and plain models. In the selected P62593 case, weighted achieves 1/16 versus plain 0/16. These views overlap and cannot be pooled.
- The new augmented model produced two scaffold-qualified P62593 backbones in a fresh 16-sample ensemble. Their first qualifying refolds have global TM 0.342 and scaffold-only TM 0.200. The qualifying designed sequences share 39.9% identity overall and retain the same supplied motif; this measures scaffold-design diversity across sequences. This establishes a two-backbone feasibility result for one selected development family, not broad conformational coverage.
- Decoder endpoint correction improved motif fits but invalidated 7/16 backbones. Closed.
- Training-only refold feedback from the improved parent yielded zero scaffold-qualified targets among 16 backbones; all eight native controls passed. Closed.

## Tests in progress

- Continuation to 8,000 updates is closed: weighted raw matches rose 3/64 to 4/64, but scaffold-qualified successes fell 1/64 to 0/64; plain also gives 0/64. Fixed global agreement improved to 7/8 plain and 6/8 weighted, without strict retention. The 6,000-update weighted model remains the reference.
- A matched weighted model receives a 50% mixture of compatible teacher endpoints where available. Original targets remain available everywhere; dropped-condition targets are unchanged. Decoder screening retained 5,227 condition/state pairs across 474 conditions. The 40-update profile verified identical initialization, all primary random draws, and every endpoint assignment. Full training completed with 2,000 matched primary draws and 14,405 audited augmented examples. Raw development matches improved 4/64 to 7/64. Complete refolding gives 1/64 scaffold-qualified successes versus 0/64 for the matched 8,000-update control; all six fixed-motif native controls passed. This ties the best 6,000-update discovery result. Fixed-panel global agreement remains 6/8 with zero strict successes.

Fresh-noise validation completed: augmented 8,000-update model gives 2/64 scaffold-qualified whole-panel successes versus 0/64 for the 6,000-update reference, and 2/16 versus 0/16 in the selected P62593 cohort. All six fixed-motif native controls pass. These views overlap and cannot be pooled. Different training exposures prevent attributing this comparison solely to augmentation.

A new correction rule rejects invalid decoded proposals. On 16 fresh paired starts, valid backbones remain 15/16 while raw motif matches rise 2/16 to 13/16; incremental correction costs 3.49 seconds total and 3.26 GiB. Numerical controls and every proposal decision passed audit. Full matched refolding is next; raw improvements do not establish designability. The original invalidating correction experiment stays closed. All panels above are development/feasibility data; locked tests remain unscored. No experimental function or physical designability claim is made.
