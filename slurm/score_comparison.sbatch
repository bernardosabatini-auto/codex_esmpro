#!/bin/bash
#SBATCH --job-name=ep_score
#SBATCH --account=bsabatini_lab
#SBATCH --partition=shared
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=00:45:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/score_%A_%a.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
RUN="runs/comparison_${1:?GPU comparison array ID required}_${SLURM_ARRAY_TASK_ID}"
exec /n/home08/bsabatini/.conda/envs/proteinae/bin/python -u scripts/score_comparison.py \
  --run "$RUN" --workers 4 --usalign runs/tools/USalign/USalign
