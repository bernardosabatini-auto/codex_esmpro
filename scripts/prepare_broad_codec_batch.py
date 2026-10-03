import argparse,json
from pathlib import Path
from broad_codec_batch_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=(a.protocol or root/'configs/fragment_broad_codec_batch_protocol.json').resolve();spec=json.loads(protocol.read_text());run=root/'runs'/spec['parent'];pm=json.loads((run/'manifest.json').read_text());c=dict(spec=spec)
    for key,path in [('protocol',protocol),('parent_manifest',run/'manifest.json'),('parent_report',root/'reports'/(run.name+'.json')),('parent_fragments',run/'fragments.h5'),('decoder_checkpoint',Path(pm['config']['decoder_checkpoint'])),('historical_fragments',Path(pm['config']['historical_fragments']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    if spec.get('failed_padding_profile'):
        path=root/'reports'/(spec['failed_padding_profile']+'.json');c['failed_padding_report']=str(path);c['failed_padding_report_sha256']=sha(path)
    audit(c);a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
