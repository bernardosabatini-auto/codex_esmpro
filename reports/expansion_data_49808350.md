# Expansion data generation

Status: complete; generation qualified: True.

Data generation controls and fixed-noise reconstruction only; full eligible-corpus reconstruction gate is required before student training.

New families: 341; metadata eligible: 63; wall seconds: 1826.4750806121156.
Exclusion counts: {'mean_confidence': 178, 'too_many_states': 69, 'excessive_state_distance': 5, 'single_state': 26}.

| Phase | Measured seconds | Peak reserved GiB |
|---|---:|---:|
| embedding | 35.08 | 24.21 |
| teacher | 1533.34 | 82.35 |
| encode_audit | 107.76 | 82.35 |

Control counts: {'controls': 4, 'embedding_controls': 4, 'rotation_controls': 4, 'metric_controls': 4}.
Reconstruction: {'targets': 63, 'priors': {'empirical': {'ca_lddt': 0.9999114075705172, 'valid': 1.0}, 'balanced': {'ca_lddt': 0.9999029249656255, 'valid': 1.0}}, 'gate_passed': True}.

Phase times include controls and exclude model loading, disk work and CPU bookkeeping; use wall time for allocation planning. Confidence/contact-state criteria exclude labels without using student outcomes. All draws are retained.
