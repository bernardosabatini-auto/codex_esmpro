"""Install the fixed functional-replay checkpoint graph after both training submissions."""
import argparse,json,subprocess
from pathlib import Path
from prepare_overfit import sha
from watch_jobs import write_json


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',nargs=2,required=True);p.add_argument('--candidate',nargs=2,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    registry={j['id']:j for j in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    ids=a.full+a.candidate
    if len(set(ids))!=4 or any(not i.isdigit() or i not in registry or registry[i]['completion_action']!='summarize_overfit' for i in ids):raise ValueError('four registered training jobs required')
    configs=[json.loads((Path(registry[i]['code_snapshot'])/'entry_configs/0.json').read_text()) for i in ids]
    if [c['seed'] for c in configs]!=[2026100171,2026100181]*2 or any(c.get('corpus_kind')!='expansion' or c['profile_only'] for c in configs) or any(c.get('functional_replay') for c in configs[:2]) or any(not c.get('functional_replay') for c in configs[2:]):raise ValueError('wrong parent order or scope')
    path=root/'runs/replay_followups.json'
    if path.exists():raise FileExistsError('inspect existing fixed graph before replacing')
    scripts=('replay_followups.py','prepare_replay_native.py','prepare_replay_ensemble.py','compare_expansion_training.py','compare_functional_replay.py','expansion_corpus.py','summarize_expansion_native.py','compare_overfit_balanced.py','evaluate_overfit_native.py','summarize_replay_native.py','generate_ensemble.py','prepare_overfit.py')
    files=[root/'scripts'/s for s in scripts]+list((root/'src').rglob('*.py'))+[root/'configs/expanded_labels_training_protocol.json',root/'configs/replay_native_protocol.json',root/'configs/functional_replay_protocol.json']+list((root/'slurm').glob('replay_native_*_h200.sbatch'))+list((root/'slurm').glob('replay_ensemble_*_rtx.sbatch'))
    plan=dict(status='active',parents=dict(full=a.full,replay=a.candidate),steps=[500,2000],code_sha256={str(p.relative_to(root)):sha(p) for p in files},scope='Fixed capacity-retaining two-endpoint native screens and up to four individually qualified external ensembles. Both seeds must retain capacity. No hypothesis selection or conversation wakeup; registered submission guard enforces totalGPU cap and deadline.')
    comparisons=root/'runs/overfit_checkpoint_analyses.json';analyses=json.loads(comparisons.read_text());spec=dict(kind='replay',jobs=ids,steps=[500,2000]);existing=[s for s in analyses['comparisons'] if s['kind']=='replay']
    if existing and existing!=[spec]:raise ValueError('different replay checkpoint plan exists')
    if not existing:analyses['comparisons'].append(spec);write_json(comparisons,analyses)
    write_json(path,plan)
    name='esm-proae-replay-followups';directory=Path.home()/'.config/systemd/user';directory.mkdir(parents=True,exist_ok=True)
    service=f'''[Unit]
Description=Fixed functional-replay endpoint follow-ups
[Service]
Type=oneshot
WorkingDirectory={root}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=PYTHONPATH={root}/src
Environment=LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib
StandardOutput=append:{root}/runs/watch/replay_followups.log
StandardError=append:{root}/runs/watch/replay_followups.log
CPUQuota=100%
MemoryMax=2G
TimeoutStartSec=300
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/replay_followups.py
'''
    timer=f'''[Unit]
Description=Check fixed functional-replay follow-ups every minute
[Timer]
OnBootSec=30s
OnUnitInactiveSec=60s
Unit={name}.service
[Install]
WantedBy=timers.target
'''
    for suffix,body in (('service',service),('timer',timer)):
        unit=directory/f'{name}.{suffix}'
        if unit.exists():raise FileExistsError('inspect existing project unit before replacing')
        unit.write_text(body)
    subprocess.run(['systemctl','--user','daemon-reload'],check=True);subprocess.run(['systemctl','--user','enable','--now',name+'.timer'],check=True);subprocess.run(['systemctl','--user','start',name+'.service'],check=True)
    print('Fixed functional-replay checkpoint and qualified-ensemble timer active.')


if __name__=='__main__':main()
