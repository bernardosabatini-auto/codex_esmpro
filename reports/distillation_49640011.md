# Ensemble-label training

Status: complete; arm: balanced; capacity profile only: False.

AFDB predicted references and ESMFold2 predicted ensembles. Full flow head trained; ProteinAE and ESMC frozen. Raw-reference and canonical-reference controls isolate pose preprocessing. Empirical and cluster-balanced arms draw 50% reference and 50% valid teacher labels; no valid teacher implies reference fallback. Clusters are not measured state populations.

| Updates | Mean CA lDDT | CA RMSD (A) | TM after Kabsch | Coarse valid |
|---|---:|---:|---:|---:|
| 0 | 0.78384 | 11.871 | 0.54529 | 0.97917 |
| 500 | 0.78572 | 11.771 | 0.52702 | 0.95312 |
| 2000 | 0.78632 | 11.636 | 0.52568 | 0.96354 |

Tuning results alone do not establish ensemble improvement. Evaluate frozen development state coverage and coarse validity, then replicate eligible effects. Confirmation and original test remain quarantined.
