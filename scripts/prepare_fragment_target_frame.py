"""Freeze anchored target construction after a qualified training-only frame probe."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];probe=root/'reports/fragment_frame_49969994.json';d=json.loads(probe.read_text());pm=root/'runs/fragment_frame_49969994/manifest.json';parent=root/'runs/fragment_training_49929751/manifest.json';m=json.loads(parent.read_text());c=dict(seed=2026100246,work_cap_seconds=780)
    if not d['target_frame_training_qualified'] or d['manifest_sha256']!=sha(pm):raise ValueError('Unqualified frame probe')
    for key,path in [('protocol',root/'configs/fragment_target_frame_protocol.json'),('probe_report',probe),('probe_manifest',pm),('parent_manifest',parent),('base_fragments',Path(m['config']['fragments'])),('decoder_checkpoint',Path(m['config']['decoder_checkpoint']))]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    if c['base_fragments_sha256']!=m['config']['fragments_sha256']:raise ValueError('Changed base data')
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
