"""Install the already declared, bounded eight-generation/eight-refold graph."""
import json
from pathlib import Path
import subprocess

from broad_fragment_followups import ARMS, CONDITIONS, advance
from prepare_overfit import sha
from watch_jobs import write_json


def main():
    root = Path(__file__).resolve().parents[1]
    campaign = json.loads((root / 'runs/current_campaign.json').read_text())
    parents = campaign['broad_training_jobs']
    jobs = json.loads((root / 'runs/jobs.json').read_text())['jobs']
    watch = json.loads((root / 'runs/watch/state.json').read_text())
    plan = dict(status='active', parents=parents,
                training_protocol_sha256=sha(root / 'configs/fragment_broad_training_protocol.json'),
                scope='Fixed final endpoints only: match2000 training draws, eight generation jobs, eight refold partitions, two CPU comparisons. No hypothesis selection or conversation wakeup. All submissions use the eight-GPU registered guard. Stop this timer on pause/revocation; retain completion monitoring.')
    result = advance(root, plan, jobs, watch, dry_run=True)
    if result['status'] != 'active':
        raise ValueError('Graph is not active')
    script_names = ('broad_fragment_followups.py', 'compare_broad_fragment_training.py',
        'prepare_extra_fragment_validation.py', 'extra_fragment_validation_core.py',
        'evaluate_extra_fragment_validation.py', 'summarize_extra_fragment_validation.py',
        'prepare_extra_fragment_refold.py', 'extra_fragment_design_panel.py',
        'evaluate_designability.py', 'fragment_refinement_core.py', 'fixed_motif_design.py',
        'summarize_extra_fragment_refold.py', 'compare_extra_fragment_refolds.py',
        'fragment_validation_core.py', 'prepare_overfit.py', 'submit_registered.py', 'watch_jobs.py')
    files = [root / 'scripts' / s for s in script_names] + list((root / 'src').rglob('*.py'))
    files += [root / 'configs' / ('fragment_broad_' + c + '_validation_protocol.json') for c in CONDITIONS]
    files += [root / 'configs/fragment_broad_refold_protocol.json', root / 'configs/fragment_broad_training_protocol.json', root / 'slurm/broad_refold_template_rtx.sbatch']
    files += [root / 'slurm' / ('broad_eval_' + c + '_' + a + '_rtx.sbatch') for c in CONDITIONS for a in ARMS]
    plan['code_sha256'] = {str(p.relative_to(root)): sha(p) for p in files}
    path = root / 'runs/broad_fragment_followups.json'
    name = 'esm-proae-broad-fragment-followups'
    directory = Path.home() / '.config/systemd/user'
    directory.mkdir(parents=True, exist_ok=True)
    if path.exists() or any((directory / (name + '.' + suffix)).exists() for suffix in ('timer', 'service')):
        raise FileExistsError('Inspect existing broad-fragment graph before replacing')
    service = f'''[Unit]
Description=Fixed broad-fragment generation and refolding follow-ups
[Service]
Type=oneshot
WorkingDirectory={root}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=PYTHONPATH={root}/src
Environment=LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib
StandardOutput=append:{root}/runs/watch/broad_fragment_followups.log
StandardError=append:{root}/runs/watch/broad_fragment_followups.log
CPUQuota=100%
MemoryMax=4G
TimeoutStartSec=900
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/broad_fragment_followups.py
'''
    timer = f'''[Unit]
Description=Check fixed broad-fragment follow-ups every fifteen seconds
[Timer]
OnBootSec=30s
OnUnitInactiveSec=15s
Unit={name}.service
[Install]
WantedBy=timers.target
'''
    write_json(path, plan)
    for suffix, body in [('service', service), ('timer', timer)]:
        (directory / (name + '.' + suffix)).write_text(body)
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', '--user', 'enable', '--now', name + '.timer'], check=True)
    subprocess.run(['systemctl', '--user', 'start', '--no-block', name + '.service'], check=True)
    print('Fixed broad-fragment follow-ups active; one guarded submission per tick.')


if __name__ == '__main__':
    main()
