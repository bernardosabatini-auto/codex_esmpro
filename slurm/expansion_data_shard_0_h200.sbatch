#!/bin/bash
#SBATCH --job-name=ep_newdata_0
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/expansion_data_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True LATENTFOLD_GPU_COUNTERS=off
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/expansion_data_${SLURM_JOB_ID}"
exec "$PYTHON" -u scripts/generate_expansion_data.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/expansion_data_shard_0.json --output "$RUN"
