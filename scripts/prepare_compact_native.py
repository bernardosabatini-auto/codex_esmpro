"""Require the complete compact probe before full-panel validation."""
import argparse,json
from pathlib import Path
import h5py,hashlib
from prepare_overfit import sha
from summarize_tensor_precision import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--probe',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    pp=a.probe/'manifest.json';probe=json.loads(pp.read_text());quality=analyze(probe,candidate='compact',micro_controls=False)
    if not quality['qualified']:raise ValueError('compact probe did not qualify')
    for key in ('selection','protocol'):
        if sha(probe['config'][key])!=probe['config'][key+'_sha256']:raise ValueError('probe input changed')
    path=a.native/'manifest.json';native=json.loads(path.read_text());c=native['config'].copy()
    if native['status']!='complete' or c.get('training_checkpoint_step',500)!=500 or c['selection_sha256']!=probe['config']['selection_sha256'] or c['evaluation_seed']!=probe['config']['evaluation_seed']:raise ValueError('incompatible source native evaluation')
    heads=[]
    for hp in probe['config']['heads']:
        h=next(h for h in c['heads'] if h['name']==hp['name'])
        if h['checkpoint_sha256']!=hp['checkpoint_sha256']:raise ValueError('probe weights differ')
        for key in ('checkpoint','training_manifest'):
            if h.get(key) and sha(h[key])!=h[key+'_sha256']:raise ValueError('head provenance changed')
        heads.append(h)
    protocol=root/'configs/compact_native_protocol.json';source=a.native/'predictions.h5'
    c.update(heads=heads,probe_manifest=str(pp.resolve()),probe_manifest_sha256=sha(pp),source_native_manifest=str(path.resolve()),source_native_manifest_sha256=sha(path),source_native_predictions=str(source.resolve()),source_native_predictions_sha256=sha(source),protocol=str(protocol),protocol_sha256=sha(protocol),work_cap_seconds=840)
    targets=json.loads(Path(c['selection']).read_text())['tuning'];c['embedding_arrays_sha256']={}
    with h5py.File(c['embedding_cache']) as cache:
        for row in targets:c['embedding_arrays_sha256'][row['id']]=hashlib.sha256(cache['tuning'][row['id']]['80'][:].tobytes()).hexdigest()
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(probe_qualified=True,heads=[h['name'] for h in heads],targets=len(targets))))


if __name__=='__main__':main()
