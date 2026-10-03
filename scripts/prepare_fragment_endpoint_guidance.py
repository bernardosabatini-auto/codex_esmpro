"""Bind the four historical families without selecting favorable starts."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from fragment_endpoint_core import audit_config


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_endpoint_guidance_protocol.json';spec=json.loads(protocol.read_text());parent=root/'runs'/spec['parent'];m=json.loads((parent/'manifest.json').read_text());pc=m['config'];c=dict(spec=spec,target_ids=pc['control_ids'],native_predictions=pc['initial_predictions'],native_predictions_sha256=pc['initial_predictions_sha256'])
    for key,path in [('protocol',protocol),('parent_manifest',parent/'manifest.json'),('parent_report',root/'reports'/(spec['parent']+'.json')),('parent_predictions',parent/'evaluation_2000.h5'),('fragments',Path(pc['fragments'])),('decoder_checkpoint',Path(pc['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    audit_config(c);a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
