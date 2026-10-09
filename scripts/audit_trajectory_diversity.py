"""All within-query scaffold pairs, before and after guidance; no filtering."""
import argparse,itertools,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates
from trajectory_guidance_core import audit
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--refold-config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.generation.resolve();mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];audit(c)
    rc=json.loads(a.refold_config.read_text())
    if m['status']!='complete' or sha(run/'predictions.h5')!=m['predictions_sha256'] or rc['generation_manifest']!=str(mp) or sha(rc['usalign'])!=rc['usalign_sha256']:raise ValueError('Changed completed sources')
    records=[];paired=[]
    with h5py.File(run/'predictions.h5',locking=False) as f,h5py.File(c['fragments'],locking=False) as fr:
        for row in c['selected']:
            ident=row['id'];q=fr['train/'+ident+'/conditions/c20_center'];mask=np.ones(row['length'],bool);st=int(q.attrs['start']);mask[st:st+20]=False
            arrays={arm:f[arm+'/'+ident+'/backbone'][:] for arm in ('baseline','guided')}
            for arm,bb in arrays.items():
                for i,j in itertools.combinations(range(4),2):records.append(dict(arm=arm,target_id=ident,bucket=row['bucket'],slots=[i,j],global_tm=usalign_coordinates(rc['usalign'],bb[i,:,1],bb[j,:,1]),scaffold_tm=usalign_coordinates(rc['usalign'],bb[i,mask,1],bb[j,mask,1])))
            for k in range(4):paired.append(dict(target_id=ident,slot=k,global_tm=usalign_coordinates(rc['usalign'],arrays['baseline'][k,:,1],arrays['guided'][k,:,1]),scaffold_tm=usalign_coordinates(rc['usalign'],arrays['baseline'][k,mask,1],arrays['guided'][k,mask,1])))
    if len(records)!=48 or len(paired)!=16:raise ValueError('Missing paired comparisons')
    summary={arm:{k:float(np.mean([r[k] for r in records if r['arm']==arm])) for k in ('global_tm','scaffold_tm')} for arm in ('baseline','guided')}
    d=dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],scorer_sha256=rc['usalign_sha256'],summary=summary,records=records,paired_displacement=paired,scope='All24 pairs perarm across4 training queries. Successful diversity requires both backbones to pass the same-valid-refold criterion; join after refolding. No independent population inference.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Mid-flow guidance raw diversity\n\n'+d['scope']+'\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n');print(json.dumps(summary))

if __name__=='__main__':main()
