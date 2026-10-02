"""Pin the original unconditional teacher and explicit synthetic noise addresses."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/unconditional_reflow_protocol.json';recipe=json.loads(protocol.read_text());parent=root/'runs/generative_pilot_49855378/manifest.json';m=json.loads(parent.read_text());h=next(h for h in m['config']['heads'] if h['name']=='original50')
    if m['status']!='complete' or sha(h['checkpoint'])!=h['checkpoint_sha256']:raise ValueError('Invalid teacher')
    c=dict(seed=recipe['label_seed'],lengths=recipe['lengths'],samples=recipe['labels_per_length'],batch=recipe['label_batch'],work_cap_seconds=780)
    for key,path in [('protocol',protocol),('parent_manifest',parent),('checkpoint',Path(h['checkpoint'])),('decoder_checkpoint',Path(m['config']['decoder_checkpoint']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Frozen2048unconditional noise/endpoint labels')

if __name__=='__main__':main()
