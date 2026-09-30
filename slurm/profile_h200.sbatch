#!/bin/bash
#SBATCH --job-name=ep_profile
#SBATCH --account=kempner_bsabatini_lab
#SBATCH --partition=kempner_h200
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --signal=B:TERM@90
#SBATCH --output=/n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot/runs/slurm_%j.out
set -euo pipefail
cd /n/netscratch/bsabatini_lab/Users/bsabatini/codex/esm_proae_reboot
export PYTHONPATH="$PWD/src"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export PYTORCH_ALLOC_CONF=expandable_segments:True
export TORCHINDUCTOR_CACHE_DIR="${TMPDIR:-/tmp}/ep_inductor_${SLURM_JOB_ID}"
PYTHON=/n/home08/bsabatini/.conda/envs/proteinae/bin/python
SOURCE=/n/netscratch/bsabatini_lab/Users/bsabatini/esm_proae
NSYS=/n/sw/helmod-rocky8/apps/Core/cuda/13.3.1-fasrc01/cuda/bin/nsys
exec "$NSYS" profile --trace=nvtx --sample=none --cpuctxsw=none \
  --gpu-metrics-devices=cuda-visible --gpu-metrics-frequency=1000 \
  --export=sqlite --output="runs/nsight_${SLURM_JOB_ID}" \
  "$PYTHON" -u scripts/profile_gpu.py --source "$SOURCE" \
  --output "runs/profile_${SLURM_JOB_ID}" --allow-gpu --minutes 24 \
  --nsys-metrics \
  --checkpoints last_pf_459M_p128x8_long512_scratch.ckpt best_lf_459M_nopair_long512_r4b.pt
