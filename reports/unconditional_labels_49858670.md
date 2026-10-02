# Unconditional teacher trajectory labels

Status: complete.

All 2048 Gaussian/endpoint/backbone triples retained, including failed coarse geometry. No sequence or experimental structure used as training input. Noise addresses differ from development generation. Generation 590.57s, peak 24.06GiB.
- Length64: 256 labels, coarse validity 0.9961.
- Length128: 256 labels, coarse validity 0.9844.
- Length192: 256 labels, coarse validity 0.9766.
- Length256: 256 labels, coarse validity 0.9883.
- Length320: 256 labels, coarse validity 0.9883.
- Length384: 256 labels, coarse validity 0.9688.
- Length448: 256 labels, coarse validity 0.9922.
- Length512: 256 labels, coarse validity 0.9883.

Every Gaussian and geometry decision was independently audited. These are model-generated labels, not biological conformational populations. Training and designability are not yet qualified.
