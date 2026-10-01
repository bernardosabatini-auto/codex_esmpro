# ATLAS metadata eligibility audit

The official [ATLAS API](https://www.dsimb.inserm.fr/ATLAS/api/docs) supplied 1,938 metadata records on 2026-10-01. The archive SHA256 is `c9cba2b7190676814bb83daf11fcfe92ad0c3a3cdaca4eb4782ca6b98c67b75e`; extracted metadata SHA256 is `844c52cbc829fb3a47bf91ecaa4209cc00be689c7ea401c814091ca68fb6ebe6`. The historical date in the archive member filename is not treated as a release identity.

Eligibility was defined before any model scoring: standard amino acids, exact metadata length, 64–512 residues, and metadata `no_contact=True` to reduce missing-partner confounds. Sixty-three chains qualify. MMseqs2 searches use identity at least 30%, coverage at least 50% of either sequence, E-value at most 1e-3, sensitivity 7.5, and two CPU threads. Candidate families are connected components, with exclusion propagated to the entire component.

All 63 candidates are separate from one another and from the current 512 training, 64 tuning, 64 probe-confirmation, full existing ensemble-candidate catalog, and original 34 locked-test sequences under this screen. Every candidate overlaps the inherited training/development exclusion corpus. Therefore this source can expand an intervention-held-out MD comparison, but it supplies **zero families for an inherited-data-disjoint generalization claim** under the current eligibility rule.

No trajectories were downloaded, no model predictions were generated, and no additional confirmation panel was selected. Any later panel requires coordinate/sequence correspondence, trajectory provenance and replicate-aware feature definitions frozen before model scoring. MD distribution matching alone must not override failed state-coverage or geometry gates.
