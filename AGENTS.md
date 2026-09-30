This project is a clean restart of the ESM-to-ProteinAE study.

- Synchronize code, tests, configuration templates, and written reports to https://github.com/bernardosabatini-auto/codex_esmpro. The user explicitly authorized commits and pushes. Exclude all data files, weights, embeddings, generated target manifests/configurations, raw result JSON, run logs, predictions, and profiler traces. Inspect the staged file list before every commit. Never force-push or alter unrelated remote work.
- Git synchronization must not block research work. Use bounded network timeouts; retain local commits and continue independent work after an authentication/network failure. Retry syncing after useful progress, without an approval loop.

- The user authorized autonomous GPU scheduling on 2026-09-29. Never exceed eight GPUs total across this project's running and pending requests. Inspect and manipulate ONLY this project's jobs recorded in runs/jobs.json, using explicit job IDs. The user has other agents working: never query their jobs or the whole user queue, cancel them, or change their files. Before each submission, check only our registered outstanding jobs. H200s are authorized; begin with measured single-GPU profiling before scaling. Do not ask for per-job permission again.
- Every submitted job must have completion monitoring. The project systemd timer `esm-proae-reboot-watch.timer` checks `runs/jobs.json` every minute. Before submitting, verify the timer is active and `runs/watch/heartbeat.json` has a successful check within two minutes; reinstall with `scripts/install_watcher.py` if needed. Register exact array task IDs immediately. For two-task comparison jobs set `completion_action` to `summarize_comparison`; this automatically validates coverage, calculates paired statistics, and summarizes GPU counters after both tasks finish. Other experiments need an appropriate explicit follow-up before submission. Read watcher events and completed reports at the start of every project turn. A tmux notification does not resume Codex reasoning; never describe the watcher as an autonomous conversation wake-up.
- Submitting an experiment is not a stopping point. Continue independent work and bounded, interruptible job checks through completion and analysis unless the user pauses or stops the task. The persistent watcher is a backup for disconnects, not a substitute for following the experiment to its result.
- Treat the original esm_proae directory as read-only. Do not import its gate scripts:
  they change directories, read environment configuration, and sometimes execute on import.
- Keep data, model weights, and the ProteinAE checkout external; record exact provenance.
- Use explicit configurations and target IDs. Fail on missing targets or invalid scores.
- Separate deployable sample selection from oracle best-of-K.
- Match sampling settings between accuracy and speed measurements.
- CPU tests use CUDA_VISIBLE_DEVICES='' and at most two numerical-library threads.
- Do not launch distributed training or install packages into the inherited environment.
