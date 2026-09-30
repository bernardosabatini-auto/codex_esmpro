#!/bin/bash
#SBATCH --job-name=ep_hybrid
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --array=0-3%4
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:20:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/hybrid_%A_%a.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
SOURCE=/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae
NSYS=/n/sw/helmod-rocky8/apps/Core/cuda/13.3.1-fasrc01/cuda/bin/nsys
MODELS=(pair pair_free pair pair_free)
POLICIES=(fp16_mlp fp16_mlp fp16_linear fp16_linear)
RUN="runs/hybrid_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
exec "$NSYS" profile --trace=nvtx --sample=none --cpuctxsw=none \
  --gpu-metrics-devices=cuda-visible --gpu-metrics-frequency=100 \
  --export=sqlite --output="${RUN}_nsight" \
  "$PYTHON" -u scripts/collect_comparison.py --source "$SOURCE" \
  --config "configs/hybrid_${POLICIES[$SLURM_ARRAY_TASK_ID]}.json" \
  --model "${MODELS[$SLURM_ARRAY_TASK_ID]}" \
  --output "$RUN" --nsys-metrics --allow-gpu \
  --score-workers 1 --usalign runs/tools/USalign/USalign
