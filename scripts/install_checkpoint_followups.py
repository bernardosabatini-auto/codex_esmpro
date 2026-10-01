"""Install the fixed final-checkpoint continuation timer for this project."""
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1];directory=Path.home()/'.config/systemd/user';directory.mkdir(parents=True,exist_ok=True)
name='esm-proae-reboot-checkpoint-followups'
service=f'''[Unit]
Description=Predeclared ESM ProteinAE checkpoint ensemble follow-ups

[Service]
Type=oneshot
WorkingDirectory={root}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib
CPUQuota=100%
MemoryMax=1G
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/checkpoint_followups.py
'''
timer=f'''[Unit]
Description=Check predeclared ESM ProteinAE continuations every minute

[Timer]
OnBootSec=30s
OnUnitInactiveSec=60s
Unit={name}.service

[Install]
WantedBy=timers.target
'''
path=directory/(name+'.service')
if path.exists() and str(root) not in path.read_text():raise ValueError('unit belongs to another project')
path.write_text(service);(directory/(name+'.timer')).write_text(timer)
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
subprocess.run(['systemctl','--user','enable','--now',name+'.timer'],check=True)
subprocess.run(['systemctl','--user','start',name+'.service'],check=True)
print('Fixed checkpoint follow-up timer active; GPU submissions retain the registered eight-GPU cap.')
