#!/bin/bash
#SBATCH --job-name=ep_extend_original
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:15:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/student_extension_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
export LATENTFOLD_GPU_COUNTERS=off
RUN="runs/student_extension_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/extend_student_ensemble.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/student_extension_original.json --output "$RUN"
