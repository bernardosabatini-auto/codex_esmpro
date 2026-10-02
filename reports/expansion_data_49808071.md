# Expansion data generation

Status: complete; generation qualified: True.

Data generation controls and fixed-noise reconstruction only; full eligible-corpus reconstruction gate is required before student training.

New families: 342; metadata eligible: 83; wall seconds: 1879.6011763350107.
Exclusion counts: {'too_many_states': 74, 'mean_confidence': 164, 'excessive_state_distance': 4, 'single_state': 17}.

| Phase | Measured seconds | Peak reserved GiB |
|---|---:|---:|
| embedding | 35.04 | 24.21 |
| teacher | 1540.55 | 82.37 |
| encode_audit | 108.51 | 82.37 |

Control counts: {'controls': 4, 'embedding_controls': 4, 'rotation_controls': 4, 'metric_controls': 4}.
Reconstruction: {'targets': 83, 'priors': {'empirical': {'ca_lddt': 0.9996359435370169, 'valid': 1.0}, 'balanced': {'ca_lddt': 0.9996175157346857, 'valid': 1.0}}, 'gate_passed': True}.

Phase times include controls and exclude model loading, disk work and CPU bookkeeping; use wall time for allocation planning. Confidence/contact-state criteria exclude labels without using student outcomes. All draws are retained.
