# Rigid-pose control precision

The 512-protein data job49978003 failed its coordinate pose check on AF-A0A7S2VM45-F1-model_v6: 0.0001564 Å versus the unchanged 0.0001 Å limit. Its latent difference was only 0.00000190. The reference/input arrays were FP32; applying translation in FP32 perturbed the geometry.

A CPU diagnostic on all512selected native center fragments found exact FP64 rotations/translations yield **bitwise-identical canonical coordinates in all512 cases**. Existing FP32 canonical coordinates differ from the FP64 baseline by at most **0.00004292 Å**, below the same limit. The correction changes only the numerical construction of the pose control. All supplied fragments retain the existing encoding recipe, and all128old inputs remain unchanged. The failed run is retained; the corrected data build uses a new run.
