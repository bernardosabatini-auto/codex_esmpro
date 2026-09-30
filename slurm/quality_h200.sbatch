#!/bin/bash
#SBATCH --job-name=ep_quality
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:15:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/quality_%A_%a.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
NSYS=/n/sw/helmod-rocky8/apps/Core/cuda/13.3.1-fasrc01/cuda/bin/nsys
RUN="runs/quality_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
exec "$NSYS" profile --trace=nvtx --sample=none --cpuctxsw=none \
 --gpu-metrics-devices=cuda-visible --gpu-metrics-frequency=100 --export=sqlite --output="${RUN}_nsight" \
 "$PYTHON" -u scripts/train_pilot.py --config runs/quality_pilot_config.json \
 --task "$SLURM_ARRAY_TASK_ID" --output "$RUN"
