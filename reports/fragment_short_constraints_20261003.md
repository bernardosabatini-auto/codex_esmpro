# Short isolated constraints

A fixed20-residue center motif produced9/256same-refold scaffold successes with conditioning and0/256with the same model's condition dropped. Successes span four of64additional development families:8/128short-chain samples and1/128long-chain samples. Raw retention was23/256versus1/256. Every raw match received exactly eight fixed-motif ProteinMPNN designs; all64native backbones received the same budget.704refolds were audited.

Native controls passed global agreement on46/64cases, primary joint retention on31/64,and the stronger scaffold criterion on29/64. These are assay controls, not a theoretical ceiling. The20-residue and30%-of-chain tasks impose different constraints; their success-rate difference is not a model improvement.

For4eyt_A, three successful backbones had pairwise scaffoldTM0.166–0.229. For7tgh_R, four had scaffoldTM0.199–0.262. These comparisons use the first qualifying refold per independently generated backbone. They demonstrate different validated scaffold designs, potentially with different full sequences, rather than conformational diversity of one fixed sequence. Yield remains low and the cohort is development data, not a blind test.

The next training comparison will add explicit short-mask coverage to both control and broader corpora. Short20-residue constraints lie below the existing20–40%training fractions for long proteins. A separately controlled loss that gives the motif a fixed share of the objective is also worth testing: weight3assigns a20/512motif only about11%of residue-loss mass, versus56%for a30%motif. This is a prospective hypothesis; no new training result is implied.
