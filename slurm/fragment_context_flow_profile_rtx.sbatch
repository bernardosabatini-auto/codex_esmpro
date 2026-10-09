#!/bin/bash
#SBATCH --job-name=ep_context_profile
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_rtx
#SBATCH --exclude=holygpu7c2313
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/fragment_context_flow_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
# Inputs are immutable; each job exclusively creates its own single-writer HDF5 output.
export HDF5_USE_FILE_LOCKING=FALSE
export LD_PRELOAD=/n/home08/bsabatini/.conda/envs/proteinae/lib/libstdc++.so.6
export LATENTFOLD_GPU_COUNTERS=dcgm
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
RUN="runs/fragment_context_flow_${SLURM_JOB_ID}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
exec "$PYTHON" -u scripts/train_fragment_context_flow.py \
 --config runs/fragment_context_flow_profile_20261009.json --output "$RUN"
