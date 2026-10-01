# Teacher-label clustering sensitivity

This exploratory audit uses only the 512 training proteins and all 8,192 existing teacher samples. It does not change the frozen labels, running experiments, or evaluation definitions.

At the original 2 A all-residue CA RMSD threshold, 426/512 targets have multiple connected components and 238/512 have sixteen singleton components. The latter receive identical empirical and cluster-balanced teacher sampling. Of the 426 multi-component targets, 412 include a singleton component. Components should not be described as established metastable states.

All frozen partitions were independently reproduced from their stored coordinates. A sensitivity analysis retained a common residue mask with mean teacher pLDDT at least 0.7 across valid conformations, requiring at least 32 retained residues. This supports a comparison for 434/512 proteins; the other 78 have insufficient confident residues. Across all targets, mean retained residue fraction is 0.6724.

For the 434 comparable proteins, mean component count falls from 10.1406 to 7.6382; 174 proteins have fewer components. All-singleton partitions fall from 200 to 128. Thus low-confidence residues contribute substantially to the apparent teacher diversity. The remaining dispersion is not automatically biologically valid state diversity: confidence filtering cannot establish populations, kinetics, or experimental correctness.

If the full pilot fails, the next label experiment should define core/contact-based diversity and confidence handling on training data before collecting more seeds. Blindly balancing global-RMSD components risks promoting flexible-tail or uncertain-structure differences. Any changed sampler requires a new matched reference control and the existing decoded-quality, geometry and state-coverage gates.
