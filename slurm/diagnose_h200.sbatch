#!/bin/bash
#SBATCH --job-name=ep_diagnose
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:10:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/diagnose_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export PYTORCH_ALLOC_CONF=expandable_segments:True
exec /n/home08/bsabatini/.conda/envs/proteinae/bin/python -u scripts/diagnose_batching.py \
  --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
  --output "runs/diagnosis_${SLURM_JOB_ID}" --allow-gpu --minutes 8 "$@"
