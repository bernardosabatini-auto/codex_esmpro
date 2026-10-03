"""Descriptive baseline diversity; no ranking, selection or gate changes."""
import argparse
import itertools
import json
from pathlib import Path
import h5py
import numpy as np
from fragment_preference_calibration import audit_generation
from latentfold.metrics import usalign_coordinates
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.generation.resolve();mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json')
    m=json.loads(mp.read_text());d=json.loads(rp.read_text());c=m['config'];audit_generation(c)
    if (m['status']!='complete' or d['status']!='complete' or d['controls']!=68
            or d['manifest_sha256']!=sha(mp) or d['predictions_sha256']!=sha(run/'predictions.h5')):
        raise ValueError('Unqualified baseline generation')
    source=root/'runs'/c['spec']['refold_profile']/'manifest.json';teacher=json.loads(source.read_text())['config']
    if sha(teacher['usalign'])!=teacher['usalign_sha256']:raise ValueError('Changed scoring binary')
    records=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['fragments']) as fr:
        for row in c['selected']:
            ident=row['id'];bb=f['new/'+ident+'/backbone'][:]
            if bb.shape!=(4,row['length'],4,3):raise ValueError('Incomplete four-noise inventory')
            q=fr['train/'+ident+'/conditions/c20_center'];mask=np.ones(row['length'],bool)
            start=int(q.attrs['start']);mask[start:start+20]=False
            for i,j in itertools.combinations(range(4),2):
                records.append(dict(target_id=ident,bucket=row['bucket'],slots=[i,j],
                                    global_tm=usalign_coordinates(teacher['usalign'],bb[i,:,1],bb[j,:,1]),
                                    scaffold_tm=usalign_coordinates(teacher['usalign'],bb[i,mask,1],bb[j,mask,1])))
    if len(records)!=192:raise ValueError('Changed diversity denominator')
    summary=[]
    for bucket in (128,256,384,512):
        rows=[r for r in records if r['bucket']==bucket]
        summary.append(dict(bucket=bucket,proteins=len({r['target_id'] for r in rows}),pairs=len(rows),
                            mean_pair_global_tm=float(np.mean([r['global_tm'] for r in rows])),
                            mean_pair_scaffold_tm=float(np.mean([r['scaffold_tm'] for r in rows]))))
    result=dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=sha(run/'predictions.h5'),
                scorer_sha256=teacher['usalign_sha256'],summary=summary,records=records,
                scope='Descriptive training-only baseline across all four noises. Lower pair TM means greater structural difference, which alone does not establish useful diversity or designability. No sample filtering or changes to prospective preference gates.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Preference collection baseline diversity\n\n```json\n'+json.dumps({k:v for k,v in result.items() if k!='records'},indent=2)+'\n```\n')
    print(json.dumps(summary))


if __name__=='__main__':main()
