"""Install the already declared, bounded eight-generation/eight-refold graph."""
import argparse,json
from pathlib import Path
import subprocess

from broad_fragment_followups import advance, graph_layout, generation_paths
from prepare_overfit import sha
from watch_jobs import write_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--study',choices=('broad','frozen','quality','cross'),default='broad');args=parser.parse_args()
    study=args.study;arms,conditions=graph_layout(study)
    root = Path(__file__).resolve().parents[1]
    campaign = json.loads((root / 'runs/current_campaign.json').read_text())
    parents = campaign[dict(cross='fragment_cross_training_jobs',frozen='frozen_generator_training_jobs',quality='fragment_quality_training_jobs',broad='broad_training_jobs')[study]]
    jobs = json.loads((root / 'runs/jobs.json').read_text())['jobs']
    watch = json.loads((root / 'runs/watch/state.json').read_text())
    training_protocol=root/dict(cross='configs/fragment_cross_training_protocol.json',frozen='configs/fragment_frozen_trunk_protocol.json',quality='configs/fragment_quality_training_protocol.json',broad='configs/fragment_broad_training_protocol.json')[study]
    plan = dict(status='active', study=study, parents=parents,
                training_protocol_sha256=sha(training_protocol),
                scope=f'Fixed final endpoints only: match2000 training draws,{len(arms)*len(conditions)} generation jobs,{4*len(conditions)} refold partitions,{len(conditions)} endpoint comparisons. No hypothesis selection or conversation wakeup. All submissions use the eight-GPU registered guard. Stop this timer on pause/revocation; retain completion monitoring.')
    result = advance(root, plan, jobs, watch, dry_run=True)
    if result['status'] != 'active':
        raise ValueError('Graph is not active')
    script_names = ('broad_fragment_followups.py', 'compare_broad_fragment_training.py',
        'prepare_extra_fragment_validation.py', 'extra_fragment_validation_core.py',
        'evaluate_extra_fragment_validation.py', 'summarize_extra_fragment_validation.py',
        'prepare_extra_fragment_refold.py', 'extra_fragment_design_panel.py',
        'evaluate_designability.py', 'fragment_refinement_core.py', 'fixed_motif_design.py',
        'summarize_extra_fragment_refold.py', 'compare_extra_fragment_refolds.py',
        'fragment_validation_core.py', 'prepare_overfit.py', 'submit_registered.py', 'watch_jobs.py',
        'designability_core.py', 'benchmark_esmfold2.py', 'teacher_numerical_recovery.py',
        'summarize_teacher_repeatability_probe.py')
    files = [root / 'scripts' / s for s in script_names] + list((root / 'src').rglob('*.py'))
    files += [root / generation_paths(study,c,arms[0])[2] for c in conditions]
    files += [root / dict(cross='configs/fragment_cross_refold_protocol.json',frozen='configs/fragment_frozen_refold_protocol.json',quality='configs/fragment_quality_refold_protocol.json',broad='configs/fragment_broad_refold_protocol.json')[study], training_protocol, root / 'slurm/broad_refold_template_rtx.sbatch']
    files += [root / generation_paths(study,c,a)[0] for c in conditions for a in arms]
    if study=='frozen':
        files += [root/'scripts'/s for s in ('compare_frozen_fragment_training.py','compare_frozen_fragment_refolds.py','broad_fragment_training.py','fragment_extension.py','train_fragment_conditioning.py','summarize_fragment_training.py')]
        files += [root/'configs/fragment_frozen_comparison_protocol.json']
    if study=='quality':
        files += [root/'scripts'/s for s in ('compare_fragment_quality_training.py','compare_frozen_fragment_refolds.py','fragment_quality_training.py','broad_fragment_training.py','fragment_extension.py','train_fragment_conditioning.py','summarize_fragment_training.py','teacher_numerical_recovery.py')]
        files += [root/'configs/fragment_quality_comparison_protocol.json']
    if study=='cross':
        files += [root/'scripts'/s for s in ('compare_fragment_cross_training.py','compare_frozen_fragment_refolds.py','fragment_cross_training.py','fragment_quality_training.py','broad_fragment_training.py','fragment_extension.py','train_fragment_conditioning.py','summarize_fragment_training.py')]
        files += [root/'configs/fragment_cross_comparison_protocol.json']
    plan['code_sha256'] = {str(p.relative_to(root)): sha(p) for p in files}
    path = root / f'runs/{study}_fragment_followups.json'
    name = f'esm-proae-{study}-fragment-followups'
    directory = Path.home() / '.config/systemd/user'
    directory.mkdir(parents=True, exist_ok=True)
    if path.exists() or any((directory / (name + '.' + suffix)).exists() for suffix in ('timer', 'service')):
        raise FileExistsError('Inspect existing broad-fragment graph before replacing')
    service = f'''[Unit]
Description=Fixed {study}-fragment generation and refolding follow-ups
[Service]
Type=oneshot
WorkingDirectory={root}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=PYTHONPATH={root}/src
Environment=LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib
StandardOutput=append:{root}/runs/watch/{study}_fragment_followups.log
StandardError=append:{root}/runs/watch/{study}_fragment_followups.log
CPUQuota=100%
MemoryMax=4G
TimeoutStartSec=900
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/broad_fragment_followups.py --study {study}
'''
    timer = f'''[Unit]
Description=Check fixed {study}-fragment follow-ups every fifteen seconds
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
    print(f'Fixed {study}-fragment follow-ups active; one guarded submission per tick.')


if __name__ == '__main__':
    main()
