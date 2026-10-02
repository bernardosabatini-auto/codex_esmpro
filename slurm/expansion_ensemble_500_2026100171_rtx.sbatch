#!/bin/bash
#SBATCH --job-name=ep_moredata_500_2026100171
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=00:15:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/ensemble_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
export LATENTFOLD_GPU_COUNTERS=off
RUN="runs/ensemble_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/generate_ensemble.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/expansion_ensemble_500_2026100171.json --output "$RUN"
