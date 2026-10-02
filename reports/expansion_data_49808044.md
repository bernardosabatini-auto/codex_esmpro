# Expansion data generation

Status: complete; generation qualified: True.

Data generation controls and fixed-noise reconstruction only; full eligible-corpus reconstruction gate is required before student training.

New families: 342; metadata eligible: 85; wall seconds: 1876.5434541339055.
Exclusion counts: {'mean_confidence': 158, 'too_many_states': 67, 'excessive_state_distance': 7, 'single_state': 25}.

| Phase | Measured seconds | Peak reserved GiB |
|---|---:|---:|
| embedding | 35.38 | 24.21 |
| teacher | 1543.00 | 82.35 |
| encode_audit | 108.60 | 82.35 |

Control counts: {'controls': 4, 'embedding_controls': 4, 'rotation_controls': 4, 'metric_controls': 4}.
Reconstruction: {'targets': 85, 'priors': {'empirical': {'ca_lddt': 0.9994817215730162, 'valid': 0.9985294117647059}, 'balanced': {'ca_lddt': 0.9995020356093786, 'valid': 0.9993966817496228}}, 'gate_passed': True}.

Phase times include controls and exclude model loading, disk work and CPU bookkeeping; use wall time for allocation planning. Confidence/contact-state criteria exclude labels without using student outcomes. All draws are retained.
