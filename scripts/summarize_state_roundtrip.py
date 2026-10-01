"""Separate reconstruction accuracy from retention of differences between states."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest')
    result=dict(status=m['status'],rows=[],caveat='Development reference reconstruction only. Nearest-state identity is a diagnostic, not experimental state coverage of de novo generation.')
    if m['status']=='complete':
        if len(m['targets'])!=16 or len(m['controls'])!=32:raise ValueError('incomplete target/control coverage')
        with h5py.File(run/'predictions.h5') as h:
            if len(h)!=16:raise ValueError('missing target groups')
            for g in h.values():
                common=g['common_indices'][:];keys=sorted(k for k in g if k!='common_indices');refs=[g[k]['reference_backbone'][:][common,1] for k in keys]
                for steps in (3,10):
                    errors=[];lddts=[];correct=[];dispersion=[];reference_distances=[];decoded_distances=[]
                    preds=[]
                    for i,k in enumerate(keys):
                        raw=g[k][f'steps{steps}'][:]
                        if raw.shape[0]!=8:raise ValueError('missing seeds')
                        pred=raw[:,common,1];preds.append(pred)
                        for x in pred:
                            distances=[ca_metrics(x,y) for y in refs];errors.append(distances[i]['ca_rmsd']);lddts.append(distances[i]['ca_lddt']);correct.append(int(np.argmin([d['ca_rmsd'] for d in distances])==i))
                        dispersion.extend(ca_metrics(pred[j],pred[k])['ca_rmsd'] for j in range(8) for k in range(j))
                    for i in range(len(refs)):
                        for j in range(i):
                            reference_distances.append(ca_metrics(refs[i],refs[j])['ca_rmsd'])
                            decoded_distances.append(float(np.mean([ca_metrics(preds[i][k],preds[j][k])['ca_rmsd'] for k in range(8)])))
                    result['rows'].append(dict(target_id=g.attrs['target_id'],family=g.attrs['family'],steps=steps,ca_rmsd=float(np.mean(errors)),ca_lddt=float(np.mean(lddts)),nearest_state_retained=float(np.mean(correct)),within_state_seed_rmsd=float(np.mean(dispersion)),reference_between_state_rmsd=float(np.mean(reference_distances)),decoded_between_state_rmsd=float(np.mean(decoded_distances))))
        metrics=('ca_rmsd','ca_lddt','nearest_state_retained','within_state_seed_rmsd','reference_between_state_rmsd','decoded_between_state_rmsd')
        result['summaries']={str(steps):{metric:float(np.mean([r[metric] for r in result['rows'] if r['steps']==steps])) for metric in metrics} for steps in (3,10)}
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Experimental-state reconstruction','',f"Status: {result['status']}.",'',result['caveat'],'','Sixteen family-distinct development proteins; eight paired decoder seeds per experimental state. Full sequence positions and missing-residue masks preserved. Reserved confirmation and original independent test were not scored.','', '| Steps | CA RMSD (A) | CA lDDT | Nearest state retained | Within-state RMSD | Reference between-state RMSD | Decoded between-state RMSD |','|---|---:|---:|---:|---:|---:|---:|']
    for steps,row in result.get('summaries',{}).items():lines.append('| '+steps+' | '+' | '.join(f'{value:.4f}' for value in row.values())+' |')
    if 'error' in result:lines+=['',result['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
