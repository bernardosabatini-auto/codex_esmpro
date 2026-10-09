# Mid-flow guidance pilot

The fixed schedule passed its prospective raw-geometry gate:15/16 guided outputs match the original motif versus3/16 baseline; both arms retain16/16 coarse-valid structures. Mean proper motifCA RMSD falls from2.120Å to0.584Å. All four training diagnostic families contribute guided matches. This is not yet a designability or generalization result.

Historical latents and backbones reproduce exactly. All four finite-difference, rigid-pose, and autograd/no-grad controls pass; frozen weights remain identical. Every saved Euler update independently replays exactly on CPU. All16outputs perarm are retained.

Job51501401 used oneRTX for58allocatedseconds; worker46.50seconds and peak13.746GiB. Guided batches of four took3.34,3.65,3.88,8.00seconds for lengths113,241,262,486, including diagnostic derivative checks and state recording. These are not production latency benchmarks. The supplied weighted utilization formula averaged28.232% over43complete recordedseconds; pre-recorder startup is excluded. No filler work was added to raise this short pilot's utilization.

Next is a fresh matched288-refold assay: all16guided,16baseline and4native backbones, eight designs each. The original motif and global/scaffold agreement must hold in the same valid refold. The gate requires at least three extra strict successes, two successful guided families, no loss in ordinary designability, and at least three passing native controls. Only then consider a broader assay and measured conditional targets for training.
