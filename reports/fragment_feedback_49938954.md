# Training-only measured designability feedback

Every candidate and refold retained. Each target comes from one valid refold meeting both motif tolerances and global agreement. Sequence-driven motif repair can produce training labels but does not convert a raw retention failure into a success. This is teacher-consistency supervision on existing training families; no development or locked-test labels.

```json
{
  "status": "complete",
  "manifest_sha256": "7833f1767119e96578c76af32f0aacde706698847a31c49fc2c6baeefe0aa585",
  "refolded_sha256": "0610c856de63f8ece61d3993e97c1e5a7e2eb6de847d5bc972fcfe9de0bb2ac5",
  "generation_manifest_sha256": "9c0493fe37e0145cae27a25f9bc3b180d42cd7ac08eb0bc76d0dd91e8da35036",
  "protocol_sha256": "44bd2d56fa0290b6c5924a1bf7c22886b20f7073cf2ce26a85553d8c223d15e2",
  "profile_qualified": true,
  "feedback_training_qualified": false,
  "profile_only": true,
  "backbones": 2,
  "completed_refolds": 16,
  "native_valid_global": 1,
  "native_count": 1,
  "generated_strict_retention": 0,
  "qualifying_feedback_backbones": 0,
  "qualifying_feedback_families": 0,
  "targets_requiring_motif_repair": 0,
  "elapsed_seconds": 140.47864060103893,
  "peak_reserved_GiB": 28.611328125
}
```
