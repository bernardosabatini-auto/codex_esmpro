# Expansion data generation

Status: complete; generation qualified: True.

Data generation controls and fixed-noise reconstruction only; full eligible-corpus reconstruction gate is required before student training.

New families: 16; metadata eligible: 5; wall seconds: 311.328354481142.
Exclusion counts: {'too_many_states': 2, 'mean_confidence': 5, 'single_state': 3, 'excessive_state_distance': 1}.

| Phase | Measured seconds | Peak reserved GiB |
|---|---:|---:|
| embedding | 4.59 | 24.01 |
| teacher | 100.44 | 82.33 |
| encode_audit | 7.37 | 82.33 |

Control counts: {'controls': 4, 'embedding_controls': 4, 'rotation_controls': 4, 'metric_controls': 4}.
Reconstruction: {'targets': 5, 'priors': {'empirical': {'ca_lddt': 0.9999901704490185, 'valid': 1.0}, 'balanced': {'ca_lddt': 0.9999916097250852, 'valid': 1.0}}, 'gate_passed': True}.

Phase times include controls and exclude model loading, disk work and CPU bookkeeping; use wall time for allocation planning. Confidence/contact-state criteria exclude labels without using student outcomes. All draws are retained.
