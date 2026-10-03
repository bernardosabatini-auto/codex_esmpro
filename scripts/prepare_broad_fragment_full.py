import argparse,json
from pathlib import Path
from broad_fragment_full_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--partition',type=int,choices=range(4),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/fragment_broad_full_protocol.json';spec=json.loads(protocol.read_text());codec=root/'runs'/spec['codec_profile'];cm=json.loads((codec/'manifest.json').read_text());source=root/'runs'/spec['source_runs'][a.partition];base=root/'runs'/spec['base_manifest'];c=dict(spec=spec,partition=a.partition,cache=str(root/'runs/recovery_data_16384/pilot.h5'))
    for key,path in [('protocol',protocol),('codec_manifest',codec/'manifest.json'),('codec_report',root/'reports'/(codec.name+'.json')),('candidates',root/'runs'/spec['candidates']/'manifest.json'),('base_manifest',base/'manifest.json'),('base_fragments',base/'fragments.h5'),('source_manifest',source/'manifest.json'),('source_backbones',source/'backbones.h5'),('decoder_checkpoint',Path(cm['config']['decoder_checkpoint']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    audit(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
