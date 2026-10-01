#!/bin/bash
#SBATCH --job-name=ep_layer_confirm
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=01:00:00
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/layer_probe_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
NSYS=/n/sw/helmod-rocky8/apps/Core/cuda/13.3.1-fasrc01/cuda/bin/nsys
RUN="runs/layer_probe_${SLURM_JOB_ID}"
exec "$NSYS" profile --trace=nvtx --sample=none --cpuctxsw=none \
 --gpu-metrics-devices=cuda-visible --gpu-metrics-frequency=100 --export=sqlite --output="${RUN}_nsight" \
 "$PYTHON" -u scripts/confirm_layer_probe.py --source /n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae \
 --config runs/layer_confirmation_config.json --output "$RUN"
