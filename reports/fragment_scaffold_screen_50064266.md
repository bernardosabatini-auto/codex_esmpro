# Agreement outside the supplied fragment

Post-hoc diagnostic with fixed residue correspondence. Default uses first qualifying refolds; --all-refolds audits the complete eight-design budget and positive controls. Supplementary scaffold joint success adds scaffold-only TM>0.5 in the SAME qualifying refold, with raw failures retained. Scaffold-only TM excludes all supplied motif residues and normalizes by scaffold length. It does not alter the preregistered strict outcome or select replacement refolds. Motif-aligned scaffold RMSD measures relative placement, including flexible deviations.

Supplementary scaffold joint backbones: {"native": 2, "weighted512": 0}

| Arm | Target / slot / sequence | Global TM | Scaffold-only TM | Scaffold lDDT | Motif-aligned scaffold RMSD |
|---|---|---:|---:|---:|---:|
| native | nmr__1BFY_1__b91a89d44751 / 0 / 0 | 0.866 | 0.773 | 0.843 | 1.80 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 1 | 0.870 | 0.768 | 0.836 | 1.56 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 2 | 0.882 | 0.798 | 0.861 | 1.72 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 3 | 0.874 | 0.792 | 0.864 | 1.83 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 4 | 0.851 | 0.760 | 0.832 | 2.03 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 5 | 0.875 | 0.789 | 0.857 | 1.65 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 6 | 0.875 | 0.786 | 0.852 | 1.82 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 7 | 0.894 | 0.814 | 0.874 | 1.51 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 0 | 0.915 | 0.903 | 0.870 | 1.87 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 1 | 0.927 | 0.916 | 0.859 | 1.75 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 2 | 0.931 | 0.922 | 0.860 | 1.47 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 3 | 0.907 | 0.893 | 0.860 | 1.88 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 4 | 0.931 | 0.924 | 0.877 | 1.44 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 5 | 0.915 | 0.912 | 0.864 | 2.10 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 6 | 0.901 | 0.904 | 0.861 | 3.11 Å |
| native | nmr__1BM5_1__17d05a87e530 / 0 / 7 | 0.919 | 0.909 | 0.863 | 1.62 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 0 | 0.602 | 0.503 | 0.605 | 5.90 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 1 | 0.799 | 0.774 | 0.811 | 2.67 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 2 | 0.847 | 0.848 | 0.908 | 2.23 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 3 | 0.811 | 0.816 | 0.898 | 2.61 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 4 | 0.804 | 0.876 | 0.921 | 7.32 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 5 | 0.794 | 0.844 | 0.928 | 5.42 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 6 | 0.796 | 0.726 | 0.767 | 2.54 Å |
| native | nmr__1CB9_1__7ca9cd6d9b60 / 0 / 7 | 0.847 | 0.847 | 0.909 | 2.21 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 0 | 0.379 | 0.429 | 0.669 | 13.99 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 1 | 0.335 | 0.401 | 0.568 | 14.15 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 2 | 0.289 | 0.374 | 0.459 | 13.67 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 3 | 0.397 | 0.460 | 0.508 | 17.65 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 4 | 0.382 | 0.445 | 0.608 | 17.73 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 5 | 0.300 | 0.379 | 0.588 | 18.26 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 6 | 0.354 | 0.388 | 0.613 | 12.24 Å |
| weighted512 | nmr__1BFY_1__b91a89d44751 / 2 / 7 | 0.319 | 0.397 | 0.564 | 17.69 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 0 | 0.404 | 0.297 | 0.426 | 23.97 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 1 | 0.694 | 0.638 | 0.673 | 15.41 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 2 | 0.472 | 0.394 | 0.433 | 14.30 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 3 | 0.682 | 0.572 | 0.609 | 13.30 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 4 | 0.682 | 0.617 | 0.616 | 12.24 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 5 | 0.779 | 0.745 | 0.738 | 7.47 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 6 | 0.415 | 0.370 | 0.455 | 13.91 Å |
| weighted512 | nmr__1BM5_1__17d05a87e530 / 1 / 7 | 0.458 | 0.384 | 0.413 | 20.50 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 0 | 0.730 | 0.790 | 0.875 | 4.34 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 1 | 0.848 | 0.814 | 0.917 | 4.00 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 2 | 0.583 | 0.675 | 0.709 | 9.14 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 3 | 0.411 | 0.439 | 0.577 | 14.75 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 4 | 0.736 | 0.823 | 0.906 | 4.03 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 5 | 0.881 | 0.820 | 0.904 | 2.99 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 6 | 0.759 | 0.792 | 0.883 | 5.21 Å |
| weighted512 | nmr__1CB9_1__7ca9cd6d9b60 / 3 / 7 | 0.386 | 0.464 | 0.638 | 14.65 Å |

Source report SHA256: `ea20b3c8b950beb8d7fbf271fab780824ade767e5175aaf158527f47bd5bc654`.
