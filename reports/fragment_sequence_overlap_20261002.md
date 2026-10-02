# Fragment development sequence-overlap screen

Development panel only; no locked sequences or structures examined. This checks overlap with the32new fine-tuning proteins, not the inherited pretraining corpus. It does not establish novelty or replace a full homology split. No panel filtering.

```json
{
  "status": "complete",
  "data_manifest_sha256": "02059dec5ca4321f31c5e5be070d88c55b1105fa9011591c692db7711dcfd5ee",
  "training_sequences": 32,
  "development_sequences": 16,
  "alignments": 512,
  "method": "BLOSUM62 global alignment, gap open10/extend.5; both all-column and shorter-sequence identity denominators; descriptive screen, not a homology certificate",
  "maximum_identity_over_alignment": 0.22077922077922077,
  "maximum_identity_over_shorter": 0.5555555555555556,
  "development_above_30percent_shorter": 15
}
```
