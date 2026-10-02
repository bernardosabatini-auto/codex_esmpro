"""Install only the declared geometry122 checkpoint and qualified-ensemble graph."""
import json
from pathlib import Path
import subprocess
from prepare_overfit import sha

root=Path(__file__).resolve().parents[1]
path=root/'runs/local_geometry_followups.json'
if path.exists():raise FileExistsError('inspect existing fixed graph before changing it')
scripts=('local_geometry_followups.py','prepare_local_geometry_native.py','prepare_local_geometry_ensemble.py','compare_local_geometry.py','compare_tail.py','compare_overfit_balanced.py','evaluate_overfit_native.py','summarize_expanded_native.py','generate_ensemble.py','prepare_overfit.py')
files=[root/'scripts'/s for s in scripts]+list((root/'src').rglob('*.py'))+[root/'configs/local_geometry122_protocol.json',root/'configs/local_geometry_native_protocol.json']+list((root/'slurm').glob('local_geometry_native_*_h200.sbatch'))+list((root/'slurm').glob('local_geometry_ensemble_*_rtx.sbatch'))
plan=dict(status='active',parents=dict(full=['49753133','49753251'],geometry=['49794011','49794064']),steps=[500,2000],code_sha256={str(p.relative_to(root)):sha(p) for p in files},scope='Two declared native screens and up to four individually quality-qualified external ensemble evaluations. No adaptive experiment choice or conversation wakeup; submit_registered enforces own-job GPU cap and user deadline.')
path.write_text(json.dumps(plan,indent=2)+'\n')
directory=Path.home()/'.config/systemd/user';directory.mkdir(parents=True,exist_ok=True)
name='esm-proae-local-geometry-followups'
service=f'''[Unit]
Description=Fixed ESM local-geometry endpoint follow-ups
[Service]
Type=oneshot
WorkingDirectory={root}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=PYTHONPATH={root}/src
Environment=LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib
StandardOutput=append:{root}/runs/watch/local_geometry_followups.log
StandardError=append:{root}/runs/watch/local_geometry_followups.log
CPUQuota=100%
MemoryMax=2G
TimeoutStartSec=300
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/local_geometry_followups.py
'''
timer=f'''[Unit]
Description=Check fixed ESM geometry follow-ups every minute
[Timer]
OnBootSec=30s
OnUnitInactiveSec=60s
Unit={name}.service
[Install]
WantedBy=timers.target
'''
for suffix,text in (('service',service),('timer',timer)):
    unit=directory/f'{name}.{suffix}'
    if unit.exists():raise FileExistsError('inspect existing project unit before replacing it')
    unit.write_text(text)
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
subprocess.run(['systemctl','--user','enable','--now',name+'.timer'],check=True)
subprocess.run(['systemctl','--user','start',name+'.service'],check=True)
print('Fixed geometry checkpoint and qualified-ensemble follow-up timer active.')
