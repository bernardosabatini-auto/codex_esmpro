#!/bin/bash
#SBATCH --job-name=ep_tail_2026100171
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/overfit_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export LATENTFOLD_GPU_COUNTERS=off
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/overfit_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/train_overfit.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/tail_training_2026100171.json --output "$RUN"
