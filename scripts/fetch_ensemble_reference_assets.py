"""Download a commit-pinned reference benchmark without installing its package."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.request


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    tree=json.loads(args.tree.read_text());commit=tree['sha']
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):raise ValueError('invalid pinned commit')
    prefixes=('bioemu_benchmarks/assets/multiconf_benchmark_0.1/', 'bioemu_benchmarks/assets/md_emulation_benchmark_0.1/')
    chosen=[r for r in tree['tree'] if r['type']=='blob' and (r['path'].startswith(prefixes) or r['path'] in ('LICENSE','README.md') or r['path'].startswith('bioemu_benchmarks/eval/md_emulation/'))]
    def fetch(row):
        rel=PurePosixPath(row['path'])
        if rel.is_absolute() or '..' in rel.parts:raise ValueError('unsafe remote path')
        path=args.output/rel;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():data=path.read_bytes()
        else:
            url=f'https://raw.githubusercontent.com/microsoft/bioemu-benchmarks/{commit}/{rel}'
            with urllib.request.urlopen(url,timeout=45) as response:data=response.read()
        actual=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        if actual!=row['sha']:raise ValueError('download does not match pinned Git blob: '+str(rel))
        if data.startswith(b'version https://git-lfs.github.com/spec'):raise ValueError('unresolved LFS pointer: '+str(rel))
        if not path.exists():path.write_bytes(data)
        return dict(path=str(rel),bytes=len(data),git_blob=actual,sha256=hashlib.sha256(data).hexdigest())
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,chosen))
    result=dict(repository='https://github.com/microsoft/bioemu-benchmarks',commit=commit,assets=rows,scope='Reference data and read-only evaluation definitions; package not installed')
    (args.output/'download_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(commit=commit,files=len(rows),bytes=sum(r['bytes'] for r in rows))))


if __name__=='__main__':main()
