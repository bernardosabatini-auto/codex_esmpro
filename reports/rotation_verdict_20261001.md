# Rotation verdict and inherited-frame correction

ProteinAE's measured latent representation is rotation-dependent: sixteen identical training structures under eight rigid poses gave latent RMS difference 0.98927. Applying the same deterministic N/CA/C frame before encoding reduced it to 0.00000198. Translation was already removed to numerical precision. This is a representation property; it does not by itself prove that rotation explains the predictor's accuracy limitation.

## Correction to the previous interpretation

The original cache was **already PCA-canonicalized**. Read-only inspection of `esm_proae/code/gate6_100k.py` and `gate8_build_afdb.py` shows `canonicalize_pyg_data` before encoding. `code/canonicalize.py` uses CA PCA axes, skewness-based signs and a right-handed determinant correction. This existing preprocessing was missed when interpreting fresh raw-reference labels as compatible with the inherited head.

Consequently, both the fresh raw-file labels and the new first-residue-frame labels differ from the inherited cache convention. The previous four-arm pilot remains a valid comparison of those label recipes, but cannot establish that the inherited pipeline had untreated arbitrary rotations. It also does not show that canonicalization in general is ineffective. Its first-residue convention was a change of convention.

The initial reference-alignment profile (49651393) preserves geometry and reconstruction, but raw-file reference latents still differ from inherited cached latents by mean RMS0.97910 on128 training proteins. Thus raw-file alignment must not be promoted as an inherited-compatible fix. After alignment to the fixed raw-file reference, externally rotated teacher inputs recover the same encoding (worst tested latent RMS difference0.00000962), confirming the alignment mechanism independently of cache compatibility.

## Corrected experiment

Recover the original reference frame directly from the inherited, sequence-mapped `ca_coords`; rigidly place the verified full reference backbone into that frame. Preserve cached reference `z` values bit-for-bit. Fit one proper global transform per teacher conformation to a shared confident core of that fixed reference, then apply it to every atom before encoding. Insufficient or degenerate cores use the predeclared all-CA fallback. No sample filtering, domain-wise fitting, coordinate averaging or latent averaging is introduced.

First verify fresh re-encoding against cached latent targets, along with all-sample reconstruction and pose controls. Then compare cached-reference-only training with cached-reference plus aligned teacher supervision using matched seeds, data, budgets and both predeclared checkpoints. No reference structure is required at inference.

Independent PCA canonicalization of each conformation can change axes/sign choices when the structure changes, particularly near eigenvalue or sign degeneracy. Aligning conformers to one fixed per-sequence reference avoids that particular change of convention. Whether this improves state coverage remains an experimental question.

For a future autoencoder redesign, explicitly enforce rotation-invariant latent codes, with reconstruction assessed up to proper rigid alignment and output pose handled separately. Ordinary rotation augmentation alone does not guarantee invariant latents. For the current pretrained model, preserve its existing convention rather than replacing it silently.

## Cached-frame verification completed

All512 training references now pass: mean re-encoding latent RMSE0.000304, maximum0.002069, after aligning full verified backbones to the cached CA coordinates. This is approximately three orders of magnitude smaller than raw-file mismatch. The actual training reference latent arrays are copied bit-for-bit rather than substituted with fresh encodings. All four label shards preserve the previous16 teacher conformations per sequence. The full8192-label reconstruction audit is job49653539.

The full reconstruction audit completed successfully: mean CA-lDDT 0.999408, mean CA RMSD 0.1953 Å, decoded coarse validity 0.991455 versus input 0.995728. Matched training jobs 49654680 (cached reference) and 49654703 (aligned empirical teacher supervision) are registered with completion analysis and final-checkpoint ensemble follow-ups. Each requests one H200 for at most 100 minutes. Accuracy benefit remains unresolved until these comparisons finish.

## Why not independently PCA-align every conformation?

Across all 8,192 already reference-aligned teacher samples, independently applying the inherited PCA/skewness convention adds a median 43.1° frame change; 39.5% exceed 90°. Even among the 1,176 samples within 1 Å aligned-core RMSD of their reference, 17.0% exceed 90°. Only 2.53% of teacher samples have near-degenerate PCA eigenvalues. These angles combine continuous axis movement and sign/axis changes; they do not establish a causal accuracy loss. The [full diagnostic](pca_frame_diagnostic_20261001.md) supports fixing one frame per sequence instead of recomputing it for each conformation. This prevents within-ensemble frame changes; it does not make the encoder invariant or remove possible frame discontinuities across sequences.
