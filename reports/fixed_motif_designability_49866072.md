# Preserve motif sequence during design

Status: complete.

Same20backbones/names/budgets. Only supplied motif residues fixed; no native scaffold sequence supplied. All160refolds and all fixed-position sequence checks audited. Experimental and teacher repeatability controls pass.

| Design | Codes | N | Original joint success | Strict refold joint success |
|---|---|---:|---:|---:|
| free | full_context | 8 | 3 | 0 |
| free | isolated | 8 | 2 | 0 |
| fixed | full_context | 8 | 2 | 2 |
| fixed | isolated | 8 | 0 | 0 |

Original joint requires valid scaffold, motif dRMS<=1A and best8scTM>.5. Strict joint also requires that SAME designed sequence refolds with scTM>.5, motif dRMS<=1A and valid geometry. Failed raw scaffolds remain failures. Four-family development feasibility only; no experimental validation or one-sequence multistability claim.
Fixed assay elapsed 219.81s,ProteinMPNN 30.85s.
