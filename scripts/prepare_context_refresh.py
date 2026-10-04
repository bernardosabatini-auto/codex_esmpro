import argparse,json
from pathlib import Path
from context_refresh_core import audit,file_stats
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',action='store_true');p.add_argument('--profile-report',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];fr=root/'runs/context_refresh_frame_50369454';fm=json.loads((fr/'manifest.json').read_text());fc=fm['config']
    c=dict(frame_config=fc,profile_only=a.profile,selected=fc['selected'] if a.profile else fc['base']['selected'],sources=[],work_cap_seconds=480 if a.profile else 1080)
    def bind(k,p):
        p=Path(p).resolve();c[k]=str(p);c['sources'].append(dict(path=str(p),sha256=sha(p)))
    for k,path in [('frame_manifest',fr/'manifest.json'),('frame_report',root/'reports/context_refresh_frame_50369454.json'),
                   ('starting_backbones',root/'runs/local_closure_canonical_full_20261004/predictions.h5')]:bind(k,path)
    if not a.profile:
        if a.profile_report is None:raise ValueError('Qualified profile report required')
        bind('profile_report',a.profile_report);pr=json.loads(a.profile_report.read_text());bind('profile_manifest',pr['manifest_path'])
        bind('profile_predictions',Path(pr['manifest_path']).parent/'predictions.h5')
    before=file_stats(c);audit(c)
    if before!=file_stats(c):raise ValueError('Sources changed during CPU content verification')
    c['cpu_verified_file_stats']=before
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('Prepared',len(c['selected']),'proteins x4noises x2models x3rounds; no refolds')


if __name__=='__main__':main()
