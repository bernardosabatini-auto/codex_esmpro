"""Freeze longest-bucket numerical controls and the two qualified checkpoints."""
import argparse,hashlib,json
from pathlib import Path
import h5py
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    native=json.loads((root/'runs/overfit_native_config.json').read_text());selection=json.loads(Path(native['selection']).read_text())
    if sha(native['selection'])!=native['selection_sha256']:raise ValueError('selection changed')
    targets=[min((r for r in selection['tuning'] if r['bucket']==length),key=lambda r:(-r['length'],r['id'])) for length in (128,256,384,512)]
    c={k:native[k] for k in ('selection','selection_sha256','embedding_cache','evaluation_seed','seed')};c['targets']=targets;c['heads']=[]
    for name,guidance in [('original',2),('aligned_teacher_balanced',1)]:
        h=next(h for h in native['heads'] if h['name']==name)
        if sha(h['checkpoint'])!=h['checkpoint_sha256']:raise ValueError('checkpoint changed')
        c['heads'].append(dict(h,guidance=guidance))
    c['embedding_arrays_sha256']={}
    with h5py.File(c['embedding_cache']) as cache:
        for row in targets:c['embedding_arrays_sha256'][row['id']]=hashlib.sha256(cache['tuning'][row['id']]['80'][:].tobytes()).hexdigest()
    protocol=root/'configs/tensor_precision_protocol.json';c.update(protocol=str(protocol),protocol_sha256=sha(protocol),work_cap_seconds=840)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps([dict(id=r['id'],length=r['length'],bucket=r['bucket']) for r in targets]))


if __name__=='__main__':main()
