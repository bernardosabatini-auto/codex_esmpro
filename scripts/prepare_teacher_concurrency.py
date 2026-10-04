import argparse
import json
from pathlib import Path
from teacher_concurrency_core import audit, file_stats, sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]; base=root/'runs/teacher_coordinates_profile_50324704'
    c=dict(original=json.loads((base/'manifest.json').read_text())['config'])
    for k,path in [('protocol',root/'configs/teacher_concurrency_protocol.json'),('reference_manifest',base/'manifest.json'),
                   ('reference_coordinates',base/'coordinates.h5'),('reference_report',root/'reports/teacher_coordinates_profile_50324704.json')]:
        c[k]=str(path);c[k+'_sha256']=sha(path)
    before=file_stats(c['original']);audit(c)
    if before!=file_stats(c['original']):raise ValueError('Dependencies changed during CPU hashing')
    c['cpu_verified_file_stats']=before
    with a.output.open('x') as f:json.dump(c,f,indent=2)
    print('CPU content verification complete; metadata bound for GPU startup')


if __name__=='__main__':main()
