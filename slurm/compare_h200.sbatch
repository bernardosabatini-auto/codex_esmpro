#!/bin/bash
#SBATCH --job-name=ep_compare
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --array=0-1%2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:45:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/compare_%A_%a.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
SOURCE=/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae
NSYS=/n/sw/helmod-rocky8/apps/Core/cuda/13.3.1-fasrc01/cuda/bin/nsys
MODELS=(pair pair_free)
MODEL="${MODELS[$SLURM_ARRAY_TASK_ID]}"
RUN="runs/comparison_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
exec "$NSYS" profile --trace=nvtx --sample=none --cpuctxsw=none \
  --gpu-metrics-devices=cuda-visible --gpu-metrics-frequency=100 \
  --export=sqlite --output="${RUN}_nsight" \
  "$PYTHON" -u scripts/collect_comparison.py --source "$SOURCE" \
  --config configs/comparison626.json --model "$MODEL" \
  --output "$RUN" --nsys-metrics --allow-gpu
