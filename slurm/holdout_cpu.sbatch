#!/bin/bash
#SBATCH --job-name=ep_holdout
#SBATCH --account=bsabatini_lab
#SBATCH --partition=shared
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/holdout_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
exec /n/home08/bsabatini/.conda/envs/proteinae/bin/python -u scripts/prepare_holdout.py \
 --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae --output "runs/holdout_${SLURM_JOB_ID}" --threads 4
