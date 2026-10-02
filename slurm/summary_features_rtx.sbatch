#!/bin/bash
#SBATCH --job-name=ep_summary_features
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:10:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/summary_features_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True LATENTFOLD_GPU_COUNTERS=off
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/summary_features_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/cache_summary_features.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/summary_features_config.json --output "$RUN"
