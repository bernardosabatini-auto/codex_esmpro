"""Prepare an inference-only 15/20-step check if both final 10-step samplers fail."""
import argparse,hashlib,json
from pathlib import Path
from reflow_quality import native_screen


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();entries=[]
    for run in a.runs:
        path=run/'manifest.json';m=json.loads(path.read_text())
        if m['status']!='complete' or m['updates']!=2000 or m['config'].get('evaluation_only'):raise ValueError('completed original training required')
        entries.append((run,path,m))
    if {m['config']['arm'] for _,_,m in entries}!={'reflow_paired','reflow_independent'}:raise ValueError('incorrect matched arms')
    configs=[{k:v for k,v in m['config'].items() if k!='arm'} for _,_,m in entries]
    if configs[0]!=configs[1]:raise ValueError('unmatched original training')
    if any(native_screen(m,2000,10)['passed'] for _,_,m in entries):raise ValueError('extension not needed: a 10-step sampler passed')
    protocol=Path('configs/reflow_extension_protocol.json').resolve()
    for run,path,m in entries:
        c=dict(m['config']);checkpoint=run/'ema_2000.ckpt'
        c.update(evaluation_only=True,sampling_steps=[15,20],work_cap_seconds=780,evaluation_protocol=str(protocol),evaluation_protocol_sha256=sha(protocol),training_manifest=str(path.resolve()),training_manifest_sha256=sha(path),evaluation_checkpoint=str(checkpoint.resolve()),evaluation_checkpoint_sha256=sha(checkpoint))
        a.output.with_name(a.output.stem+'_'+c['arm']+'.json').write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
