# Expansion data generation

Status: complete; generation qualified: True.

Data generation controls and fixed-noise reconstruction only; full eligible-corpus reconstruction gate is required before student training.

New families: 342; metadata eligible: 69; wall seconds: 1794.705977665726.
Exclusion counts: {'mean_confidence': 179, 'too_many_states': 62, 'single_state': 28, 'excessive_state_distance': 4}.

| Phase | Measured seconds | Peak reserved GiB |
|---|---:|---:|
| embedding | 34.82 | 24.21 |
| teacher | 1541.02 | 82.39 |
| encode_audit | 108.34 | 82.39 |

Control counts: {'controls': 4, 'embedding_controls': 4, 'rotation_controls': 4, 'metric_controls': 4}.
Reconstruction: {'targets': 69, 'priors': {'empirical': {'ca_lddt': 0.9997228236086126, 'valid': 1.0}, 'balanced': {'ca_lddt': 0.9997448800898002, 'valid': 1.0}}, 'gate_passed': True}.

Phase times include controls and exclude model loading, disk work and CPU bookkeeping; use wall time for allocation planning. Confidence/contact-state criteria exclude labels without using student outcomes. All draws are retained.
