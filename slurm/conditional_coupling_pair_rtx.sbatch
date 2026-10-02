#!/bin/bash
#SBATCH --job-name=ep_coupling_pair
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --exclude=holygpu7c2313
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/conditional_coupling_%A_%a.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True LATENTFOLD_GPU_COUNTERS=off
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/conditional_coupling_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
if [[ "$SLURM_ARRAY_TASK_ID" == "0" ]]; then
 exec "$PYTHON" -u scripts/train_overfit.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae --config runs/conditional_coupling_independent.json --output "$RUN"
elif [[ "$SLURM_ARRAY_TASK_ID" == "1" ]]; then
 exec "$PYTHON" -u scripts/train_overfit.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae --config runs/conditional_coupling_optimal.json --output "$RUN"
else
 exit 2
fi
