# Additional-family generation results

The teacher-endpoint augmentation signal did not generalize to the additional64-family development panel. Stop further mixture or duration sweeps on this recipe.

| Training proteins | Matched control | Augmented targets |
|---|---:|---:|
|128|1/256|0/256|
|512|2/256|0/256|

Counts require the same valid refold to retain the supplied motif within1Å properCA RMSD and dRMS, agree globally atTM>0.5, and agree on the scaffold alone atTM>0.5. All1024generated samples remain in the denominators. Every raw match received exactly eight motif-fixed ProteinMPNN designs; all64native backbones received a separate shared eight-design positive-control budget. Total1216refolds. Primary and stronger scaffold counts were identical. The successful control samples span one and two families respectively; these small counts do not establish a replicated effect.

Native controls passed global designability on45/64families, but only17/64passed the strict same-refold motif/scaffold criterion. Thus the center30%-of-chain task is difficult even with experimental backbones. A20-residue-center task is being evaluated separately, with conditioned and condition-dropped sampling from the same frozen512-protein control model and identical noises. This changes the task, not the accuracy of an existing model. For long chains20residues is outside the existing20–40%training-mask range; a negative result will need to distinguish input coverage from general inability to condition.

The second route is broader supervision. A CPU sequence audit selected7680additional training families plus the unchanged512base proteins, targeting8192total. A64-case source-verification pilot recovered complete AFDB backbones with exact sequence/residue correspondence. Full encoding parity and crop roundtrips must pass before broader construction or training; no new teacher labeling is planned. Every new source must be verified before geometry supervision.

This is additional development replication, not a blind test: the experimental corpus had previously been used by the original project for prediction-model development. No current evaluation outputs enter training, and locked tests remain unscored. Raw failures were not refolded, so their unconstrained global designability is unknown.

Evidence: `fragment_extra64_augmentation_comparison.json`; fourgeneration assays50113435/50113475/50113526/50113594; fourrefolding assays50114647/50114694/50114767/50114824. Code and written reports are synchronized; data remain excluded fromGit.
