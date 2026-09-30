This project is a clean restart of the ESM-to-ProteinAE study.

- Synchronize code, tests, configuration templates, and written reports to https://github.com/bernardosabatini-auto/codex_esmpro. The user explicitly authorized commits and pushes. Exclude all data files, weights, embeddings, generated target manifests/configurations, raw result JSON, run logs, predictions, and profiler traces. Inspect the staged file list before every commit. Never force-push or alter unrelated remote work.
- Git synchronization must not block research work. Use bounded network timeouts; retain local commits and continue independent work after an authentication/network failure. Retry syncing after useful progress, without an approval loop.

- The user authorized autonomous GPU scheduling on 2026-09-29. Never exceed eight GPUs total across this project's running and pending requests. Inspect and manipulate ONLY this project's jobs recorded in runs/jobs.json, using explicit job IDs. The user has other agents working: never query their jobs or the whole user queue, cancel them, or change their files. Before each submission, check only our registered outstanding jobs. H200s are authorized; begin with measured single-GPU profiling before scaling. Do not ask for per-job permission again.
- Treat the original esm_proae directory as read-only. Do not import its gate scripts:
  they change directories, read environment configuration, and sometimes execute on import.
- Keep data, model weights, and the ProteinAE checkout external; record exact provenance.
- Use explicit configurations and target IDs. Fail on missing targets or invalid scores.
- Separate deployable sample selection from oracle best-of-K.
- Match sampling settings between accuracy and speed measurements.
- CPU tests use CUDA_VISIBLE_DEVICES='' and at most two numerical-library threads.
- Do not launch distributed training or install packages into the inherited environment.
