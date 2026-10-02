# Original retry output-equivalence diagnostic

Status:complete. Unchanged0.2A/0.99 controls, exact selected indices and geometry decisions. All original eight latency families and every K1/8/32 prefix retained.

| Comparison | Draws | Failed | Max CA RMSD | Min CA lDDT |
|---|---:|---:|---:|---:|
| cached_vs_reference_1 | 8 | 0 | 0.000059 | 1.000000 |
| cached_vs_reference_8 | 64 | 0 | 0.000742 | 1.000000 |
| cached_vs_reference_32 | 256 | 0 | 0.000000 | 1.000000 |
| online_vs_reference_1 | 8 | 0 | 0.000402 | 1.000000 |
| online_vs_reference_8 | 64 | 0 | 0.002729 | 1.000000 |
| online_vs_reference_32 | 256 | 1 | 0.238339 | 0.993370 |
| online_vs_cached_1 | 8 | 0 | 0.000383 | 1.000000 |
| online_vs_cached_8 | 64 | 0 | 0.002751 | 1.000000 |
| online_vs_cached_32 | 256 | 1 | 0.238339 | 0.993370 |
| cached_prefix_vs32_1 | 8 | 0 | 0.000059 | 1.000000 |
| cached_prefix_vs32_8 | 64 | 0 | 0.000742 | 1.000000 |
| online_prefix_vs32_1 | 8 | 0 | 0.000155 | 1.000000 |
| online_prefix_vs32_8 | 64 | 0 | 0.000347 | 1.000000 |

{"target_id": "nmr__1BFY_1__b91a89d44751", "kind": "online_vs_reference", "count": 32, "slot": 18, "selected_draw": 18, "reference_draw": 18, "validity_identical": true, "ca_rmsd": 0.2383388026934795, "tm_after_kabsch": 0.990419862945804, "ca_lddt": 0.9933701657458563}

{"target_id": "nmr__1BFY_1__b91a89d44751", "kind": "online_vs_cached", "count": 32, "slot": 18, "selected_draw": 18, "reference_draw": 18, "validity_identical": true, "ca_rmsd": 0.2383388026934795, "tm_after_kabsch": 0.990419862945804, "ca_lddt": 0.9933701657458563}

Online versus cached ESM differences:
- ood60__P50405__67632888e82e: RMSE4.8748948e-06, max absolute6.9618225e-05.
- crypticpocket__P61586__aeabcc544d6c: RMSE2.1612134e-06, max absolute4.196167e-05.
- crypticpocket__P08037__b8cdcf0b572c: RMSE3.0182996e-06, max absolute6.7710876e-05.
- crypticpocket__Q16658__6d919890c9e7: RMSE2.97413e-06, max absolute5.8412552e-05.
- md_emulation__cath1_3udcA02__0175a90823bb: RMSE4.1479475e-06, max absolute6.1035156e-05.
- md_emulation__cath1_3luyA02__33e7c503c257: RMSE6.4220626e-06, max absolute0.00016689301.
- nmr__1BFY_1__b91a89d44751: RMSE6.6825987e-06, max absolute0.00014877319.
- nmr__1BM5_1__17d05a87e530: RMSE2.7668395e-06, max absolute4.7445297e-05.

This diagnosis cannot relax the original control or promote a candidate. Batch-prefix and online-embedding effects are separated; failed latency49852006 remains failed. No independent-test scoring.
