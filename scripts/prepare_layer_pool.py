"""Export a bounded training-only candidate pool for family-isolated layer probes."""
import argparse,hashlib,json
from pathlib import Path
import h5py


def main():
    p=argparse.ArgumentParser()
    for name in ('dataset','manifest','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();source=json.loads(a.manifest.read_text());selected=[]
    for bucket in (128,256,384,512):
        rows=[r for r in source['records'] if r['bucket']==bucket]
        rows.sort(key=lambda r:hashlib.sha256(('layer-pool-20261001:'+r['id']).encode()).hexdigest());selected.extend(rows[:512])
    if len(selected)!=2048:raise ValueError('need 512 candidates per length bucket')
    with h5py.File(a.dataset) as h:
        for row in selected:
            g=h['train'][row['id']];seq=g.attrs['sequence'];seq=seq.decode() if isinstance(seq,bytes) else str(seq)
            if hashlib.sha256(seq.encode()).hexdigest()!=row['sequence_sha256']:raise ValueError('sequence changed')
            row['sequence']=seq
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(status='candidates_only',dataset=str(a.dataset.resolve()),source_manifest_sha256=hashlib.sha256(a.manifest.read_bytes()).hexdigest(),records=selected),indent=2)+'\n')
    a.output.with_suffix('.fasta').write_text(''.join('>'+r['id']+'\n'+r['sequence']+'\n' for r in selected));print('Exported',len(selected),'training candidates; no structures scored')


if __name__=='__main__':main()
