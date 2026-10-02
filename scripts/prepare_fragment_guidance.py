"""Bind one guidance-strength screen to the audited distance conditioner."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=root/'runs/fragment_training_49911511';manifest=run/'manifest.json';report=root/'reports/fragment_training_49911511.json';m=json.loads(manifest.read_text());d=json.loads(report.read_text());old=m['config']
    if m['status']!='complete' or m['updates']!=2000 or old.get('distance_precision')!='fp64' or old.get('auxiliary_motif') or d['manifest_sha256']!=sha(manifest):raise ValueError('Wrong completed conditioner')
    c=dict(seed=2026100211,guidance=[1,2],samples=4,steps=50,control_ids=old['control_ids'],work_cap_seconds=360)
    for key,path in [('generation_manifest',manifest),('training_report',report),('checkpoint',run/'ema_2000.ckpt'),('fragments',Path(old['fragments'])),('parent_predictions',run/'evaluation_2000.h5'),('decoder_checkpoint',Path(old['decoder_checkpoint'])),('protocol',root/'configs/fragment_guidance_protocol.json')]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
