# Torsion closure qualifies for designability testing

The fixed CPU construction passes the full physical gate on **61/128 generated
scaffolds**, spanning26families. All128candidates remain in the denominator.
All15previously proven geometric obstructions remain failures. The native oracle
passes124/128; its four failures are exactly the four original native-parent cases
that already fail the absolute peptide-edge criterion. No GPU was used.

The native result is a construction sanity check, not learned capacity: the
original parent provides local geometry and starting torsions. A zero-correction
predictor can already do well when the native parent and requested motif agree.
Future training must include nontrivial generated-parent/fragment conflicts and
must be evaluated against the zero-correction and solver controls.

The method preserves generated-parent bond lengths, bond angles and peptide omega,
changes phi/psi in eight residues on each side of the isolated20residue fragment,
and keeps the actual motif and far scaffold fixed. It uses one prescribed torsion
optimization start. Both endpoint triplets are explicit constraints, and the final
gate scores the actual assembled coordinates rather than hypothetical ghost atoms.

| Full panel | Generated | Native oracle |
|---|---:|---:|
| Coarse validity |74/128|128/128|
| Local molecular geometry |101/128|128/128|
| Every eight-flank peptide/CA edge valid |111/128|124/128|
| Joint physical eligibility |61/128|124/128|

Both precisions passed the512-bridge numerical preflight;12unit tests passed.
The32-output feasibility profile yielded12/16generated and16/16native successes.
Every profile output exactly repeats in the full assay. Independent final audit
reconstructed all256stored outputs from recorded torsions with zero discrepancy
and independently rescored actual molecular geometry. All numerical controls passed.

For a fair geometric comparison, both methods were scored over **all eight flank
residues**. The older Cartesian prediction plus four-residue local repair passes
0/128generated and0/128native under that expanded molecular-geometry criterion.
Its previously reported30/128generated result used a four-residue local geometry
check plus eight-flank peptide-edge checks; that historical result is unchanged.
Do not describe61versus30as a comparison under identical gates. Against the newly
matched eight-flank criterion, the generated difference is47.66percentage points,
family-bootstrap95% interval36.72–58.59. Multiple construction choices differ, so
this is not a one-variable ablation or a gain attributable to learning.

Full CPU wall time548.17s, including controls and scoring; solver time468.12s over
256cases. Generated cases take mean2.67s, median2.84s each. This cost must be added
to original parent generation, and is a reason to train a faster conditional model
only if the outputs prove useful. It is not yet a fast learned solution.

## Next: actual designability, then training

`configs/torsion_closure_refold_protocol.json` binds the next assay: all128generated
outputs ×8fixed-motif ProteinMPNN sequences, unchanged FP32 teacher sampling,
reused historical parent/experimental controls, and strict same-refold motif,
global/scaffold and covalent agreement. Geometry failures are not filtered out.
No native-oracle construction outputs are refolded as candidate successes.

The existing decoder-refold exporter deliberately rejects this new endpoint. Add a
separate closure exporter/auditor and a narrowly scoped worker branch. Move the
teacher/input hash scan to CPU preflight; validate bound file identity at GPU
startup/end, and rehash during CPU completion audit. Preserve existing execution
and sequence budgets. Four one-RTX partitions with35minute caps fit the measured
teacher workload and eight-GPU total cap. No refolding jobs have been submitted yet.

Only a positive matched designability result licenses a separate training protocol
using these constructions as potential supervision. The project objective remains
explicit isolated-fragment training, generative diversity and designability—not
CPU geometry repair alone. Locked tests remain unused.

Evidence: `torsion_closure_full_20261004.json`,
`torsion_closure_full_audit_20261004.json`, `torsion_geometry_comparison_20261004.json`.
Full report SHA256:18dced564834de25b4f33a7d85c870c490078265f666191ccd697fe68f8815bc.
Full predictions SHA256:ace4159e7a323e7df9b91b0ceaf6035a8f34096ef6eceecf50ca98eedc02c0cd.
