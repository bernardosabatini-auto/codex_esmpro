#!/bin/bash
#SBATCH --job-name=ep_ens_reflow_independent_500_10
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=00:15:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/ensemble_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
NSYS=/n/sw/helmod-rocky8/apps/Core/cuda/13.3.1-fasrc01/cuda/bin/nsys
RUN="runs/ensemble_${SLURM_JOB_ID}"
exec "$NSYS" profile --trace=nvtx --sample=none --cpuctxsw=none \
 --gpu-metrics-devices=cuda-visible --gpu-metrics-frequency=100 --export=sqlite --output="${RUN}_nsight" \
 "$PYTHON" -u scripts/generate_ensemble.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/ensemble_trained_reflow_independent_500_10.json --output "$RUN"
