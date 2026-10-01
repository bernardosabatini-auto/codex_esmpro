# Original training-state audit

Checkpoint SHA256: `241ec496e222fd52a43d88e4eede1b1885027ab70d8f796fcb4a5197800985c0`. Epoch 30, update 63235.

All 469 parameter tensors (464,123,272 parameters) have finite raw weights, EMA weights, and shape-matched finite optimizer moments. Moment variances are nonnegative and every step counter agrees.

State-dict parameter order exactly matches local named_parameters; one saved group with complete shape-matched moments.

Original AdamW betas (0.9, 0.95); current learning rate 0.00012485921256325826; original EMA decay 0.999. The previous pilots used a fresh optimizer, EMA weights as their initialization, and EMA decay 0.99.

Relative L2 distance between original raw and EMA weights: 0.031143.

The legacy checkpoint saves CPU and data-order RNG only, not CUDA RNG or a fully specified original distributed data stream. Loading raw weights, EMA and optimizer is a state-restored continuation, not an exact replay.

A follow-up must isolate the effect of restoring optimizer moments from changing initial weights, loss reduction, learning rate, or data. Use identical raw initialization and frozen pilot settings for a fresh-versus-restored optimizer pair. Keep the original EMA as a separate starting state only when shared by both arms. Do not call this an exact training resume.
