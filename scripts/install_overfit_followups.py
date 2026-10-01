"""Install the fixed own-project capacity-test handoff; no adaptive experiments."""
import json,subprocess
from pathlib import Path
from prepare_overfit import sha

root=Path(__file__).resolve().parents[1]
plan=root/'runs/overfit_followups.json'
if plan.exists():raise FileExistsError('Existing plan must be inspected rather than overwritten')
plan.write_text(json.dumps(dict(label_job='49693246',protocol_sha256=sha(root/'configs/overfit_reliable_protocol.json'),purpose_prefix='reliable32 capacity20261001',deadline_utc='2026-10-02T15:00:00+00:00'),indent=2)+'\n')
folder=Path.home()/'.config/systemd/user';folder.mkdir(exist_ok=True,parents=True)
(folder/'esm-proae-overfit-followups.service').write_text(f'''[Unit]
Description=Declared ESM teacher-capacity experiment handoff
[Service]
Type=oneshot
WorkingDirectory={root}
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/overfit_followups.py
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=PYTHONPATH={root}/src
StandardOutput=append:{root}/runs/overfit_followups.log
StandardError=append:{root}/runs/overfit_followups.log
TimeoutStartSec=180
''')
(folder/'esm-proae-overfit-followups.timer').write_text('''[Unit]
Description=Check declared capacity-test prerequisites every30seconds
[Timer]
OnActiveSec=5
OnUnitActiveSec=30
AccuracySec=1
[Install]
WantedBy=timers.target
''')
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
subprocess.run(['systemctl','--user','enable','--now','esm-proae-overfit-followups.timer'],check=True)
print('Installed fixed gated graph; completion watcher remains responsible for job summaries')
