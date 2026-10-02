"""Install the fixed427-family checkpoint graph after both training submissions."""
import argparse,json,subprocess
from pathlib import Path
from prepare_overfit import sha
from watch_jobs import write_json


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--jobs',nargs=2,required=True);p.add_argument('--native-gpu',choices=('h100','h200'),required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    registry={j['id']:j for j in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if len(set(a.jobs))!=2 or any(not i.isdigit() or i not in registry or registry[i]['completion_action']!='summarize_overfit' for i in a.jobs):raise ValueError('two registered training jobs required')
    configs=[json.loads((Path(registry[i]['code_snapshot'])/'entry_configs/0.json').read_text()) for i in a.jobs]
    if [c['seed'] for c in configs]!=[2026100171,2026100181] or any(c.get('corpus_kind')!='expansion' or c['profile_only'] for c in configs):raise ValueError('wrong parent order or scope')
    path=root/'runs/expansion_followups.json'
    if path.exists():raise FileExistsError('inspect existing fixed graph before replacing')
    scripts=('expansion_followups.py','prepare_expansion_native.py','prepare_expansion_ensemble.py','compare_expansion_training.py','expansion_corpus.py','compare_overfit_balanced.py','evaluate_overfit_native.py','summarize_expansion_native.py','generate_ensemble.py','prepare_overfit.py')
    files=[root/'scripts'/s for s in scripts]+list((root/'src').rglob('*.py'))+[root/'configs/expanded_labels_training_protocol.json',root/'configs/expansion_native_protocol.json']+list((root/'slurm').glob(f'expansion_native_*_{a.native_gpu}.sbatch'))+list((root/'slurm').glob('expansion_ensemble_*_rtx.sbatch'))
    plan=dict(status='active',parents=dict(expansion=a.jobs),steps=[500,2000],native_gpu=a.native_gpu,code_sha256={str(p.relative_to(root)):sha(p) for p in files},scope='Fixed two-endpoint native screens and up to four individually qualified external ensemble evaluations. No hypothesis selection or conversation wakeup; registered submission guard enforces totalGPU cap and deadline.')
    comparisons=root/'runs/overfit_checkpoint_analyses.json';analyses=json.loads(comparisons.read_text());spec=dict(kind='expansion',jobs=a.jobs,steps=[500,2000]);existing=[s for s in analyses['comparisons'] if s['kind']=='expansion']
    if existing and existing!=[spec]:raise ValueError('different expansion checkpoint plan exists')
    if not existing:analyses['comparisons'].append(spec);write_json(comparisons,analyses)
    write_json(path,plan)
    name='esm-proae-expansion-followups';directory=Path.home()/'.config/systemd/user';directory.mkdir(parents=True,exist_ok=True)
    service=f'''[Unit]
Description=Fixed larger-data endpoint follow-ups
[Service]
Type=oneshot
WorkingDirectory={root}
Environment=CUDA_VISIBLE_DEVICES=
Environment=OMP_NUM_THREADS=1
Environment=MKL_NUM_THREADS=1
Environment=OPENBLAS_NUM_THREADS=1
Environment=PYTHONPATH={root}/src
Environment=LD_LIBRARY_PATH=/n/home08/bsabatini/.conda/envs/proteinae/lib
StandardOutput=append:{root}/runs/watch/expansion_followups.log
StandardError=append:{root}/runs/watch/expansion_followups.log
CPUQuota=100%
MemoryMax=2G
TimeoutStartSec=300
ExecStart=/n/home08/bsabatini/.conda/envs/proteinae/bin/python {root}/scripts/expansion_followups.py
'''
    timer=f'''[Unit]
Description=Check fixed larger-data follow-ups every minute
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
    print('Fixed larger-data checkpoint and qualified-ensemble timer active.')


if __name__=='__main__':main()
