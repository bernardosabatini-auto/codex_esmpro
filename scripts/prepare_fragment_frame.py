"""Freeze a training-only probe of supplied-fragment target frames."""
import argparse,json
from pathlib import Path
import h5py
from prepare_overfit import sha
from prepare_fragment_feedback import selected_ids


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];parent=root/'runs/fragment_training_49929751/manifest.json';m=json.loads(parent.read_text());old=m['config'];c=dict(seed=2026100245,work_cap_seconds=480,conditions=['f30_left','f30_center','f30_right'])
    for key,path in [('protocol',root/'configs/fragment_frame_probe_protocol.json'),('parent_manifest',parent),('fragments',Path(old['fragments'])),('decoder_checkpoint',Path(old['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if m['status']!='complete' or c['fragments_sha256']!=old['fragments_sha256']:raise ValueError('Invalid source')
    with h5py.File(c['fragments']) as f:c['training_ids']=selected_ids(f)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
