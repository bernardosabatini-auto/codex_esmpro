# Training-only measured designability feedback

Every candidate and refold retained. Each target comes from one valid refold meeting both motif tolerances and global agreement. Sequence-driven motif repair can produce training labels but does not convert a raw retention failure into a success. This is teacher-consistency supervision on existing training families; no development or locked-test labels.

```json
{
  "feedback_revision": "weighted6000_scaffold",
  "native_scaffold_valid_global": 8,
  "status": "complete",
  "manifest_sha256": "f86f4a6644de8492da78b347575e006475f9853e718bb7153b05e6dbb009c29c",
  "refolded_sha256": "4f79c4c193ddf9ce99fa1bc364c04e781cc8cdcb0748ab17d6d393a36d79e095",
  "generation_manifest_sha256": "99d95e43a8745ddd4f7bf9a4e4549f58905bdc64991a63ae7ede7109f322b09d",
  "protocol_sha256": "d4ff728c62d6c8c997fffa30ec6b6caac541d7182ad0cd15552377d7a394fa87",
  "profile_qualified": false,
  "feedback_training_qualified": false,
  "profile_only": false,
  "backbones": 24,
  "completed_refolds": 192,
  "native_valid_global": 8,
  "native_count": 8,
  "generated_strict_retention": 1,
  "qualifying_feedback_backbones": 0,
  "qualifying_feedback_families": 0,
  "targets_requiring_motif_repair": 0,
  "elapsed_seconds": 545.666659463197,
  "peak_reserved_GiB": 28.625
}
```
