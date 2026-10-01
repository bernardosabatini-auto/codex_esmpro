# Alternating sequence-to-selected-backbone comparison

Status: rejected_numerical_controls.

The planned comparison assigns 626 development proteins across four deterministic shards, with three alternating repeats of both pipelines on each GPU. Planned timings include CPU sample selection. Repeats are not extra targets or independent inference noise. Dual ESMC residency increases memory above standalone deployment. Numerical controls must pass before timing begins.

{'run': 'runs/matched_online_49612272_0', 'error': 'ValueError: ValueError: candidate online batch/padding control failed'}
{'run': 'runs/matched_online_49612272_1', 'error': 'ValueError: ValueError: candidate online batch/padding control failed'}
{'run': 'runs/matched_online_49612272_2', 'error': 'ValueError: Cancelled after other shards failed required numerical controls; no timed passes started.'}
{'run': 'runs/matched_online_49612272_3', 'error': 'ValueError: Cancelled after other shards failed required numerical controls; no timed passes started.'}

| Task | Variant | Length bucket | CA RMSD (A) | Cross-prediction CA lDDT | Native CA lDDT absolute change |
|---|---|---:|---:|---:|---:|
| matched_online_49612272_0 | candidate | 256 | 0.332677 | 0.980455 | 0.001775 |
| matched_online_49612272_1 | candidate | 128 | 2.223638 | 0.757244 | 0.010064 |

Required bounds: RMSD <=0.2 A, cross-prediction CA lDDT >=0.99, native CA lDDT absolute change <=0.005. The candidate is rejected under these unchanged bounds. No repeated throughput or selected-accuracy result is available.

The 34 independent-test structures remain unscored. No optimized ESMFold2 throughput comparison is claimed.
