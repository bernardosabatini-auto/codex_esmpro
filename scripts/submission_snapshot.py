"""Freeze committed source and the script's entry configuration before submission."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


def freeze_submission(root,script,commit):
    root=Path(root).resolve();script=Path(script).resolve()
    subprocess.run(['git','diff','--quiet','HEAD','--','src','scripts','slurm'],cwd=root,check=True)
    configs={}
    body=script.read_text()
    for relative in re.findall(r'--config\s+([^\s\\]+)',body):
        path=(root/relative).resolve()
        configs[relative]=path.read_bytes()
    payload=body.encode()+b''.join(k.encode()+v for k,v in sorted(configs.items()))
    key=hashlib.sha256(payload).hexdigest()[:16]
    target=root/'runs/code_snapshots'/f'{commit[:12]}_{key}'
    if (target/'submission.json').exists():return target/'submitted.sbatch',target
    target.mkdir(parents=True,exist_ok=False)
    archive=target/'source.tar'
    # Reports and tests are not worker inputs. Extracting hundreds of historical
    # reports on shared storage dominated guarded submission time. Runtime code,
    # protocols, batch scripts and provenance still come from the exact commit;
    # generated entry configurations remain frozen separately below.
    top=subprocess.check_output(['git','ls-tree','--name-only',commit],cwd=root,text=True).splitlines()
    runtime=[name for name in top if name not in ('reports','tests','.gitignore')]
    subprocess.run(['git','archive','--format=tar','--output',str(archive),commit,'--',*runtime],cwd=root,check=True)
    subprocess.run(['tar','-xf',str(archive),'-C',str(target)],check=True);archive.unlink()
    (target/'reports').mkdir(exist_ok=True)
    (target/'runs').symlink_to(root/'runs',target_is_directory=True)
    # Generated development configuration files are ignored by Git but required
    # by a few entry points. Preserve them with this source revision as well.
    if (root/'configs').exists():
        (target/'configs').mkdir(exist_ok=True)
        for path in (root/'configs').iterdir():
            if path.is_file() and not (target/'configs'/path.name).exists():shutil.copyfile(path,target/'configs'/path.name)
    marker='cd '+str(root)
    if marker not in body:raise ValueError('batch script does not use the expected project working directory')
    body=body.replace(marker,'cd '+str(target))
    (target/'entry_configs').mkdir()
    for index,(relative,contents) in enumerate(sorted(configs.items())):
        frozen=target/'entry_configs'/f'{index}.json';frozen.write_bytes(contents)
        body=body.replace('--config '+relative,'--config '+str(frozen))
    (target/'submitted.sbatch').write_text(body)
    (target/'submission.json').write_text(json.dumps(dict(commit=commit,original_script=str(script),
        config_sha256={k:hashlib.sha256(v).hexdigest() for k,v in configs.items()}),indent=2)+'\n')
    return target/'submitted.sbatch',target
