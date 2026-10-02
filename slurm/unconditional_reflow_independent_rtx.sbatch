#!/bin/bash
#SBATCH --job-name=ep_uncond_independent
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --exclude=holygpu7c2313
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/unconditional_reflow_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export LATENTFOLD_GPU_COUNTERS=off
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/unconditional_reflow_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/train_unconditional_reflow.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/unconditional_reflow_independent_config.json --output "$RUN"
