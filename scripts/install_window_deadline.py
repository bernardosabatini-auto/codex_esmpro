"""Install a one-shot deadline for this project's bounded autonomous session."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import socket
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--window',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1];window_path=args.window.resolve()
    if root/'runs' not in window_path.parents:raise ValueError('window must be inside this project runs directory')
    window=json.loads(window_path.read_text());deadline=datetime.fromisoformat(window['deadline'].replace('Z','+00:00'))
    name='esm-proae-autonomous-deadline-'+deadline.strftime('%Y%m%d')
    units=Path.home()/'.config/systemd/user';units.mkdir(parents=True,exist_ok=True)
    quote=lambda value:json.dumps(str(value).replace('%','%%'))
    command=' '.join(map(quote,[sys.executable,root/'scripts/close_autonomous_window.py','--root',root,'--window',window_path]))
    (units/(name+'.service')).write_text(f'''[Unit]
Description=Close the registered ESM ProteinAE autonomous work window
ConditionHost={socket.gethostname()}
StartLimitIntervalSec=0

[Service]
Type=oneshot
ExecStart={command}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
CPUQuota=100%
MemoryMax=256M
TimeoutStartSec=120
Restart=on-failure
RestartSec=15
''')
    (units/(name+'.timer')).write_text(f'''[Unit]
Description=Stop unfinished project requests at the authorized window deadline
ConditionHost={socket.gethostname()}

[Timer]
OnCalendar={deadline.strftime('%Y-%m-%d %H:%M:%S')} UTC
AccuracySec=1s
Persistent=true
Unit={name}.service

[Install]
WantedBy=timers.target
''')
    subprocess.run(['systemctl','--user','daemon-reload'],check=True,timeout=30)
    subprocess.run(['systemctl','--user','enable','--now',name+'.timer'],check=True,timeout=30)
    print(subprocess.check_output(['systemctl','--user','show',name+'.timer','-p','ActiveState','-p','NextElapseUSecRealtime'],text=True,timeout=10))


if __name__=='__main__':main()
