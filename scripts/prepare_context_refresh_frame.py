import argparse,json
from pathlib import Path
from context_refresh_frame_core import audit,file_stats
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    base=json.loads((root/'runs/compatible_fragment_20261004.json').read_text())
    c=dict(base=base,sources=[],work_cap_seconds=480)
    for key,path in [('protocol',root/'configs/fragment_context_refresh_protocol.json'),
                     ('compatible_report',root/'reports/compatible_fragment_50364419.json')]:
        c[key]=str(path);c['sources'].append(dict(path=str(path),sha256=sha(path)))
    c['spec']=json.loads(Path(c['protocol']).read_text())
    c['selected']=[next(r for r in base['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    before=file_stats(c);audit(c)
    if file_stats(c)!=before:raise ValueError('Sources changed during CPU verification')
    c['cpu_verified_file_stats']=before
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Four proteins x four noises x generated/native frame controls; no training or refolds')


if __name__=='__main__':main()
