# Matched unconditional trajectory compression

Both arms use identical labels, initial weights and every logged target/time/dropout/LR draw; independent versus recorded Gaussian coupling is the sole declared training difference. All raw generation failures retained.

| Arm | Step | Raw validity | Mapping CA-lDDT | Geometry screen |
|---|---:|---:|---:|---|
| paired | 0 | 0.2969 | 0.5177 | False |
| paired | 500 | 0.9375 | 0.4630 | False |
| paired | 1000 | 0.8906 | 0.4810 | False |
| independent | 0 | 0.2969 | 0.5177 | False |
| independent | 500 | 0.1875 | 0.4918 | False |
| independent | 1000 | 0.1406 | 0.4854 | False |

Step0 paired minus independent validity +0.0000,95%family interval [0.0, 0.0].

Step500 paired minus independent validity +0.7500,95%family interval [0.625, 0.859375].

Step1000 paired minus independent validity +0.7500,95%family interval [0.65625, 0.84375].

A geometry-qualified checkpoint still requires the matched motif/ProteinMPNN assay. Mapping fidelity is descriptive; changing the correspondence between Gaussian draws and outputs can preserve a distribution. No conditional-folding, designability or new biological-state claim. No independent tests scored.
