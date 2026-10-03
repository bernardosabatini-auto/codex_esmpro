import argparse,json
from pathlib import Path
from prepare_overfit import sha
from extra_fragment_data import audit_config


def main():
    p=argparse.ArgumentParser();p.add_argument('--selection',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];selection=a.selection.resolve();d=json.loads(selection.read_text());parent=json.loads((root/'runs/fragment_training_50043086/manifest.json').read_text())['config'];protocol=root/'configs/fragment_extra_encoding_protocol.json';c=dict(spec=json.loads(protocol.read_text()),target_ids=sorted(r['target_id'] for r in d['selected']),control_ids=parent['control_ids'])
    for key,path in [('selection',selection),('backbones',selection.parent/'backbones.h5'),('protocol',protocol),('decoder_checkpoint',Path(parent['decoder_checkpoint'])),('historical_fragments',Path(parent['fragments']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
