"""Bind the numerical-solver screen to the existing tuning baseline."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    m=json.loads(a.baseline.read_text());c=m['config']
    if m['status']!='complete' or len([r for r in m['scores'] if r['step']==0 and r['sampling_steps']==25])!=192:raise ValueError('complete original tuning baseline required')
    if sha(c['selection'])!=c['selection_sha256']:raise ValueError('selection changed')
    d={k:c[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed')}
    d.update(baseline_manifest=str(a.baseline.resolve()),baseline_manifest_sha256=sha(a.baseline),checkpoint_sha256=m['checkpoint']['sha256'],protocol=str(a.protocol.resolve()),protocol_sha256=sha(a.protocol),work_cap_seconds=780)
    a.output.write_text(json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
