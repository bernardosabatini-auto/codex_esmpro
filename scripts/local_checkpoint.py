"""Stage only hash-bound model files into a job-owned local temporary directory."""
import hashlib
from pathlib import Path


def copy_verified(source,destination,expected):
    digest=hashlib.sha256()
    with Path(source).open('rb') as src,Path(destination).open('xb') as dst:
        while block:=src.read(8*1024*1024):
            digest.update(block);dst.write(block)
    if digest.hexdigest()!=expected:
        Path(destination).unlink()
        raise ValueError('Checkpoint changed during local staging')


def stage_checkpoint(path,sources,directory):
    path=Path(path).resolve();bound={str(Path(r['path']).resolve()):r['sha256'] for r in sources}
    required=[path];metadata=Path(str(path)+'.meta.json')
    if metadata.exists():required.append(metadata)
    if any(str(p) not in bound for p in required):raise ValueError('Unbound checkpoint or architecture sidecar')
    directory=Path(directory);directory.mkdir(exist_ok=False)
    for p in required:copy_verified(p,directory/p.name,bound[str(p)])
    return directory/path.name
