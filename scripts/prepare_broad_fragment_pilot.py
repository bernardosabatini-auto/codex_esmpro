import argparse,json
from pathlib import Path
from broad_fragment_pilot import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_broad_pilot_protocol.json';spec=json.loads(protocol.read_text());parent=json.loads((root/'runs/fragment_training_50043086/manifest.json').read_text())['config'];c=dict(spec=spec,control_ids=parent['control_ids'],cache=str(root/'runs/recovery_data_16384/pilot.h5'))
    for key,path in [('protocol',protocol),('candidates',root/'runs'/spec['selection']/'manifest.json'),('selection',root/'runs/broad_fragment_pilot_selection.json'),('source_manifest',root/'runs'/spec['source_verification']/'manifest.json'),('backbones',root/'runs'/spec['source_verification']/'backbones.h5'),('decoder_checkpoint',Path(parent['decoder_checkpoint'])),('historical_fragments',Path(parent['fragments']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    audit(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
