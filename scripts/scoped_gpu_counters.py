"""Resolve DCGM through registered Slurm allocation and verify GPU UUID."""
import json,re,subprocess
from pathlib import Path


def physical_gpu(details):
    matches=re.findall(r'(?:^|\s)GRES=gpu:[^\s]*\(IDX:(\d+)\)(?=\s|$)',details)
    if len(matches)!=1:raise ValueError('Exactly one physical GPU in scoped Slurm allocation required')
    return matches[0]


def assigned_dcgm_gpu(root,job_id,uuid,dcgmi):
    registry=json.loads((Path(root)/'runs/jobs.json').read_text())['jobs']
    own={i:j for j in registry for i in ([j['id']]+j.get('tasks',[]))}
    if job_id not in own or own[job_id].get('gpus_per_task',own[job_id]['gpus'])!=1:
        raise ValueError('DCGM requires one registered own GPU allocation')
    details=subprocess.run(['scontrol','show','job','-d','-o',job_id],check=True,capture_output=True,text=True,timeout=5).stdout
    index=physical_gpu(details)
    identity=subprocess.run([dcgmi,'discovery','--gpuid',index,'--info','a'],check=True,capture_output=True,text=True,timeout=5).stdout
    found=set(re.findall(r'GPU-[0-9a-fA-F-]+',identity))
    if found!={uuid}:raise ValueError('DCGM identity differs from assigned CUDA GPU')
    return index,identity
