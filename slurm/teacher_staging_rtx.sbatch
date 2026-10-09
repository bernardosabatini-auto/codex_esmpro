#!/bin/bash
#SBATCH --job-name=ep_teacher_staging
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --exclude=holygpu7c2313
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=00:15:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/teacher_concurrency_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export HDF5_USE_FILE_LOCKING=FALSE
export LD_PRELOAD=/n/home08/bsabatini/.conda/envs/proteinae/lib/libstdc++.so.6
export LATENTFOLD_GPU_COUNTERS=dcgm
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/teacher_concurrency_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/teacher_staging.py --config runs/teacher_staging_20261009.json --output "$RUN"
