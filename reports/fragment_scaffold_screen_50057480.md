# Agreement outside the supplied fragment

Post-hoc diagnostic with fixed residue correspondence. Default uses first qualifying refolds; --all-refolds audits the complete eight-design budget and positive controls. Supplementary scaffold joint success adds scaffold-only TM>0.5 in the SAME qualifying refold, with raw failures retained. Scaffold-only TM excludes all supplied motif residues and normalizes by scaffold length. It does not alter the preregistered strict outcome or select replacement refolds. Motif-aligned scaffold RMSD measures relative placement, including flexible deviations.

Supplementary scaffold joint backbones: {"native": 3, "plain": 1, "weighted": 2}

| Arm | Target / slot / sequence | Global TM | Scaffold-only TM | Scaffold lDDT | Motif-aligned scaffold RMSD |
|---|---|---:|---:|---:|---:|
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 0 | 0.986 | 0.974 | 0.950 | 0.78 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 1 | 0.984 | 0.971 | 0.942 | 0.76 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 2 | 0.986 | 0.976 | 0.939 | 0.75 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 3 | 0.988 | 0.977 | 0.941 | 0.67 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 4 | 0.985 | 0.972 | 0.943 | 0.75 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 5 | 0.988 | 0.979 | 0.957 | 0.69 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 6 | 0.989 | 0.981 | 0.942 | 0.62 Å |
| native | crypticpocket__P61586__aeabcc544d6c / 0 / 7 | 0.986 | 0.976 | 0.939 | 0.74 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 0 | 0.994 | 0.992 | 0.978 | 0.68 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 1 | 0.993 | 0.991 | 0.973 | 0.72 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 2 | 0.994 | 0.992 | 0.970 | 0.61 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 3 | 0.985 | 0.975 | 0.934 | 1.05 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 4 | 0.993 | 0.991 | 0.978 | 0.88 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 5 | 0.990 | 0.984 | 0.968 | 0.84 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 6 | 0.995 | 0.992 | 0.981 | 0.56 Å |
| native | crypticpocket__P62593__3e6631cbb03c / 0 / 7 | 0.994 | 0.992 | 0.974 | 0.67 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 0 | 0.860 | 0.766 | 0.860 | 1.95 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 1 | 0.851 | 0.734 | 0.820 | 1.71 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 2 | 0.884 | 0.805 | 0.866 | 1.66 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 3 | 0.903 | 0.828 | 0.871 | 1.62 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 4 | 0.859 | 0.769 | 0.850 | 1.89 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 5 | 0.834 | 0.731 | 0.823 | 1.80 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 6 | 0.874 | 0.793 | 0.871 | 1.74 Å |
| native | nmr__1BFY_1__b91a89d44751 / 0 / 7 | 0.875 | 0.786 | 0.847 | 1.80 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 0 | 0.652 | 0.734 | 0.871 | 5.33 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 1 | 0.454 | 0.533 | 0.819 | 11.91 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 2 | 0.450 | 0.484 | 0.500 | 29.42 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 3 | 0.430 | 0.458 | 0.698 | 13.46 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 4 | 0.692 | 0.762 | 0.893 | 4.86 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 5 | 0.888 | 0.841 | 0.931 | 1.39 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 6 | 0.571 | 0.585 | 0.829 | 8.35 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 0 / 7 | 0.311 | 0.412 | 0.507 | 26.36 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 0 | 0.224 | 0.279 | 0.606 | 17.42 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 1 | 0.377 | 0.332 | 0.664 | 10.45 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 2 | 0.361 | 0.328 | 0.642 | 20.40 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 3 | 0.307 | 0.321 | 0.712 | 16.27 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 4 | 0.396 | 0.308 | 0.607 | 18.22 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 5 | 0.409 | 0.318 | 0.635 | 15.84 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 6 | 0.231 | 0.276 | 0.618 | 19.64 Å |
| plain | nmr__1BFY_1__b91a89d44751 / 2 / 7 | 0.245 | 0.301 | 0.638 | 24.46 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 0 | 0.554 | 0.447 | 0.488 | 15.01 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 1 | 0.621 | 0.499 | 0.643 | 14.87 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 2 | 0.500 | 0.317 | 0.535 | 17.62 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 3 | 0.562 | 0.493 | 0.670 | 15.16 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 4 | 0.646 | 0.517 | 0.603 | 11.38 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 5 | 0.479 | 0.358 | 0.431 | 18.91 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 6 | 0.537 | 0.427 | 0.482 | 14.97 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 1 / 7 | 0.673 | 0.554 | 0.638 | 9.21 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 0 | 0.418 | 0.241 | 0.413 | 22.79 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 1 | 0.446 | 0.424 | 0.549 | 17.44 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 2 | 0.475 | 0.269 | 0.397 | 22.36 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 3 | 0.576 | 0.439 | 0.543 | 22.15 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 4 | 0.466 | 0.322 | 0.447 | 12.16 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 5 | 0.392 | 0.238 | 0.384 | 19.81 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 6 | 0.455 | 0.260 | 0.415 | 15.94 Å |
| weighted | crypticpocket__P61586__aeabcc544d6c / 3 / 7 | 0.493 | 0.464 | 0.547 | 17.45 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 0 | 0.625 | 0.468 | 0.587 | 21.63 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 1 | 0.584 | 0.407 | 0.500 | 18.17 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 2 | 0.618 | 0.451 | 0.544 | 13.16 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 3 | 0.600 | 0.428 | 0.544 | 19.26 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 4 | 0.477 | 0.333 | 0.491 | 17.57 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 5 | 0.605 | 0.433 | 0.569 | 17.97 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 6 | 0.402 | 0.204 | 0.394 | 27.81 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 1 / 7 | 0.623 | 0.460 | 0.585 | 18.39 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 0 | 0.331 | 0.298 | 0.454 | 35.97 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 1 | 0.677 | 0.538 | 0.617 | 14.24 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 2 | 0.665 | 0.524 | 0.600 | 14.18 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 3 | 0.365 | 0.469 | 0.560 | 31.99 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 4 | 0.620 | 0.449 | 0.553 | 13.75 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 5 | 0.509 | 0.441 | 0.527 | 20.73 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 6 | 0.648 | 0.495 | 0.570 | 16.02 Å |
| weighted | crypticpocket__P62593__3e6631cbb03c / 7 / 7 | 0.648 | 0.505 | 0.557 | 16.26 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 0 | 0.315 | 0.292 | 0.585 | 16.48 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 1 | 0.373 | 0.388 | 0.630 | 17.42 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 2 | 0.431 | 0.457 | 0.668 | 14.44 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 3 | 0.348 | 0.245 | 0.460 | 19.81 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 4 | 0.241 | 0.278 | 0.497 | 16.93 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 5 | 0.391 | 0.410 | 0.640 | 18.11 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 6 | 0.365 | 0.332 | 0.640 | 18.14 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 0 / 7 | 0.462 | 0.387 | 0.597 | 6.82 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 0 | 0.196 | 0.207 | 0.395 | 19.61 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 1 | 0.249 | 0.324 | 0.491 | 21.97 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 2 | 0.267 | 0.344 | 0.510 | 23.00 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 3 | 0.193 | 0.195 | 0.388 | 17.13 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 4 | 0.264 | 0.243 | 0.477 | 15.30 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 5 | 0.240 | 0.296 | 0.451 | 27.32 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 6 | 0.302 | 0.338 | 0.521 | 21.63 Å |
| weighted | nmr__1BFY_1__b91a89d44751 / 2 / 7 | 0.307 | 0.351 | 0.529 | 19.02 Å |

Source report SHA256: `25c030592db9d8811f171373f16ce380381ed8939046f6d47aa013f149d6d9e2`.
