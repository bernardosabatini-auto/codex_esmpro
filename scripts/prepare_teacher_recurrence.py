"""CPU provenance checks for fresh teacher samples on the frozen training panel."""
import argparse,json
from pathlib import Path
import h5py
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--labels',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();m=json.loads(a.labels.read_text());labels=a.labels.parent/'labels.h5'
    if m['status']!='complete' or not m['training_gate_passed'] or sha(labels)!=m['labels_sha256']:raise ValueError('audited label source required')
    rows=m['config']['targets']
    if len(rows)!=32 or len({r['id'] for r in rows})!=32:raise ValueError('expected frozen32 panel')
    seeds={};artifacts=None
    for path in sorted({r['source_labels'] for r in rows}):
        expected={r['source_labels_sha256'] for r in rows if r['source_labels']==path}
        if expected!={sha(path)}:raise ValueError('teacher source labels changed')
        source=json.loads((Path(path).parent/'manifest.json').read_text())
        if artifacts is None:artifacts=source['config']['teacher_artifacts']
        if source['config']['teacher_artifacts']!=artifacts:raise ValueError('different teacher artifacts')
        with h5py.File(path) as h:
            for r in rows:
                if r['source_labels']==path:seeds[r['id']]=int(h[r['id']].attrs['seed'])
    checked=[]
    for artifact in artifacts:
        path=Path(artifact['path'])
        if sha(path)!=artifact['sha256']:raise ValueError('teacher artifact hash changed')
        stat=path.stat();checked.append(dict(artifact,bytes=stat.st_size,mtime_ns=stat.st_mtime_ns))
        print('verified',path.name,flush=True)
    protocol=json.loads(a.protocol.read_text())
    config=dict(label_manifest=str(a.labels.resolve()),label_manifest_sha256=sha(a.labels),labels_sha256=m['labels_sha256'],
                protocol=str(a.protocol.resolve()),protocol_sha256=sha(a.protocol),teacher_seeds=seeds,
                teacher_artifacts=checked,seed=protocol['seed'],samples=32,sample_batch=16,steps=50,work_cap_seconds=1380)
    a.output.write_text(json.dumps(config,indent=2)+'\n')


if __name__=='__main__':main()
