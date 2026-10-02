"""Freeze complete experimental development references without outcome selection."""
import argparse,hashlib,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/generative_pilot_protocol.json';recipe=json.loads(protocol.read_text())
    source=json.loads((root/'runs/retry_prefix_diagnostic_config.json').read_text());panel=Path(source['panel']);rows=json.loads(panel.read_text())['development'];eligible=[]
    if sha(panel)!=source['panel_sha256']:raise ValueError('Changed panel')
    for row in rows:
        for index,ref in enumerate(row['references']):
            if ref['observed_indices']==list(range(row['length'])) and not ref['mismatched_sequence_positions']:
                if sha(ref['path'])!=ref['sha256']:raise ValueError('Changed experimental source')
                eligible.append(dict(target_id=row['query_id'],family=row['family'],length=row['length'],sequence=row['sequence'],reference_index=index,reference=ref));break
    order=lambda r:hashlib.sha256(r['family'].encode()).hexdigest()
    short=sorted([r for r in eligible if r['length']<=128],key=order)[:8];long=sorted([r for r in eligible if r['length']>128],key=order)[:8];chosen=short+long
    if len(short)!=8 or len(long)!=8 or len({r['family'] for r in chosen})!=16:raise ValueError('Incomplete panel')
    selection=root/'runs/generative_pilot_selection.json';selection.write_text(json.dumps(dict(rows=chosen),indent=2)+'\n')
    c=dict(samples=recipe['samples'],seed=recipe['seed'],modes=recipe['modes'],work_cap_seconds=1080,control_ids=[r['target_id'] for r in short[:2]+long[:2]])
    for key,path in [('protocol',protocol),('selection',selection),('panel',panel),('embedding_cache',Path(source['embedding_cache'])),('decoder_checkpoint',Path(source['decoder_checkpoint']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    heads=json.loads((root/'runs/reflow_retry_native_config.json').read_text())['heads'];c['heads']=[]
    for name,oldname in [('original50','original'),('reflow10','reflow10')]:
        h=next(h for h in heads if h['name']==oldname)
        if sha(h['checkpoint'])!=h['checkpoint_sha256']:raise ValueError('Changed checkpoint')
        c['heads'].append(dict(name=name,steps=recipe['heads'][name],checkpoint=h['checkpoint'],checkpoint_sha256=h['checkpoint_sha256']))
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen16families, lengths',min(r['length'] for r in chosen),max(r['length'] for r in chosen),'controls',c['control_ids'])

if __name__=='__main__':main()
