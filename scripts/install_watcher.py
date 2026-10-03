"""Install this project's per-user systemd watcher on the current host."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--python', type=Path, default=Path(sys.executable))
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    watch = root/'runs/watch'
    watch.mkdir(parents=True, exist_ok=True)
    config = dict(python=str(a.python.resolve()), host=socket.gethostname())
    if os.environ.get('TMUX') and os.environ.get('TMUX_PANE'):
        config.update(tmux_socket=os.environ['TMUX'].split(',')[0], tmux_pane=os.environ['TMUX_PANE'])
        config['tmux_session'] = subprocess.run(['tmux', '-S', config['tmux_socket'], 'display-message', '-p',
            '-t', config['tmux_pane'], '#{session_id}'], capture_output=True, text=True, check=True, timeout=3).stdout.strip()
    (watch/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    # Shared home directories: only this host executes this project's timer.
    # No changes to lingering policy, other services, cron, or other agents.
    units = Path.home()/'.config/systemd/user'
    units.mkdir(parents=True, exist_ok=True)
    name = 'esm-proae-reboot-watch'
    def quoted(value):
        return '"'+str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%')+'"'
    service = f'''[Unit]
Description=ESM ProteinAE project completion analysis watcher
ConditionHost={socket.gethostname()}

[Service]
Type=oneshot
WorkingDirectory={str(root).replace('%', '%%')}
ExecStart={quoted(a.python.resolve())} {quoted(root/'scripts/watch_jobs.py')} --root {quoted(root)}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
Nice=10
CPUQuota=100%
MemoryMax=1G
TimeoutStartSec=2100
'''
    timer = '''[Unit]
Description=Check only ESM ProteinAE registered jobs every minute

[Timer]
OnActiveSec=2s
OnUnitInactiveSec=60s
AccuracySec=1s
Unit=esm-proae-reboot-watch.service

[Install]
WantedBy=timers.target
'''
    (units/f'{name}.service').write_text(service)
    (units/f'{name}.timer').write_text(timer)
    for args in [['daemon-reload'], ['enable', '--now', name+'.timer'], ['start', name+'.service']]:
        subprocess.run(['systemctl', '--user', *args], check=True, timeout=300)
    print(json.dumps(dict(service=name, host=socket.gethostname(), interval_seconds=60, config=str(watch/'config.json'))))


if __name__ == '__main__':
    main()
