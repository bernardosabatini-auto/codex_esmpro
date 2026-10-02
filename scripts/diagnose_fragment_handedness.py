"""Describe proper versus reflection-allowed motif fits without changing gates."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha


def fits(x,y):
    x=np.asarray(x,dtype=np.float64);y=np.asarray(y,dtype=np.float64);x=x-x.mean(0);y=y-y.mean(0);u,_,vt=np.linalg.svd(x.T@y);sign=float(np.linalg.det(u@vt));fix=np.eye(3);fix[-1,-1]=sign
    return dict(proper_rmsd=float(np.sqrt(np.mean(np.sum((x@(u@fix@vt)-y)**2,axis=-1)))),unrestricted_rmsd=float(np.sqrt(np.mean(np.sum((x@(u@vt)-y)**2,axis=-1)))),unrestricted_reflects=sign<0)


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sources=[];rows=[]
    for run in a.runs:
        m=json.loads((run/'manifest.json').read_text())
        if m['status']!='complete':raise ValueError('Completed source required')
        c=m['config'];path=run/('predictions.h5' if run.name.startswith('fragment_guidance_') else 'evaluation_2000.h5');sources.append(dict(run=str(run),manifest_sha256=sha(run/'manifest.json'),predictions_sha256=sha(path)))
        with h5py.File(path) as f,h5py.File(c['fragments']) as fragments:
            groups=['guidance1','guidance2'] if run.name.startswith('fragment_guidance_') else ['development/conditioned']
            for group in groups:
                for ident,g in f[group].items():
                    q=fragments['development/'+ident+'/conditions/f30_center'];st=int(q.attrs['start']);ref=q['fragment'][:,1];bb=g['backbone'][:]
                    for k,x in enumerate(bb):rows.append(dict(run=run.name,group=group,target_id=ident,slot=k,**fits(x[st:st+len(ref),1],ref)))
    summaries=[]
    for run,group in sorted({(r['run'],r['group']) for r in rows}):
        rr=[r for r in rows if (r['run'],r['group'])==(run,group)];summaries.append(dict(run=run,group=group,samples=len(rr),reflection_preferred=sum(r['unrestricted_reflects'] for r in rr),reflection_gain_over_1A=sum(r['proper_rmsd']-r['unrestricted_rmsd']>1 for r in rr),reflection_only_below_1A=sum(r['unrestricted_rmsd']<=1 and r['proper_rmsd']>1 for r in rr),mean_proper_rmsd=float(np.mean([r['proper_rmsd'] for r in rr])),mean_unrestricted_rmsd=float(np.mean([r['unrestricted_rmsd'] for r in rr]))))
    d=dict(status='complete',interpretation='Diagnostic only. Reflection-allowed fitting is never a success criterion; threshold and designability requirements unchanged.',sources=sources,summaries=summaries,records=rows);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fragment handedness diagnostic\n\nReflection-allowed fits diagnose an ambiguity of distance inputs; they never qualify a scaffold. All development samples retained.\n\n```json\n'+json.dumps(dict(d,records='See ignored raw JSON'),indent=2)+'\n```\n');print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
