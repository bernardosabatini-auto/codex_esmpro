# Training-only measured designability feedback

Every candidate and refold retained. Each target comes from one valid refold meeting both motif tolerances and global agreement. Sequence-driven motif repair can produce training labels but does not convert a raw retention failure into a success. This is teacher-consistency supervision on existing training families; no development or locked-test labels.

```json
{
  "status": "complete",
  "manifest_sha256": "73dc1bf3e485f17ababb6df50e70f1eae18f13fa5a6b739f4abe4b5f3bf585f8",
  "refolded_sha256": "519d1666ab07ffc45a21e9aef95295f76f4f96cb6662dca25f4ce74b1cf11515",
  "generation_manifest_sha256": "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
  "protocol_sha256": "44bd2d56fa0290b6c5924a1bf7c22886b20f7073cf2ce26a85553d8c223d15e2",
  "profile_qualified": false,
  "feedback_training_qualified": false,
  "profile_only": false,
  "backbones": 24,
  "completed_refolds": 192,
  "native_valid_global": 8,
  "native_count": 8,
  "generated_strict_retention": 1,
  "qualifying_feedback_backbones": 2,
  "qualifying_feedback_families": 2,
  "targets_requiring_motif_repair": 1,
  "elapsed_seconds": 663.7666499060579,
  "peak_reserved_GiB": 28.625
}
```
