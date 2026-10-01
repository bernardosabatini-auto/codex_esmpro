"""Validate seed/step coverage and report teacher dispersion and sampling cost."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from summarize_ensemble import rmsd
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='No manifest')
    result=dict(status=m['status'],rows=[],scope='ESMFold2-Fast structure-only sampling with validated trunk reuse. Seeds are repeated draws, integration steps are not physical trajectory frames. Dispersion alone does not demonstrate state coverage.')
    if m['status']=='complete':
        c=m['config'];ids=c['target_ids']
        if len(m['targets'])!=len(ids) or len(m['controls'])!=len(ids):raise ValueError('incomplete targets/controls')
        with h5py.File(run/'predictions.h5') as h:
            if set(h)!=set(ids):raise ValueError('target mismatch')
            for ident,g in h.items():
                if set(g)!={f'steps{s}' for s in c['steps']}:raise ValueError('step coverage mismatch')
                for steps in c['steps']:
                    bb=g[f'steps{steps}']['backbone'][:]
                    if len(bb)!=32 or not np.isfinite(bb).all():raise ValueError('sample coverage mismatch')
                    ca=bb[:,:,1];peptide=np.linalg.norm(bb[:,:-1,2]-bb[:,1:,0],axis=-1)
                    result['rows'].append(dict(target_id=ident,steps=steps,pairwise_ca_rmsd=float(np.mean([rmsd(ca[i],ca[j]) for i in range(32) for j in range(i)])),peptide_outlier_fraction=float(np.mean((peptide<1.1)|(peptide>1.6)))))
        result['summaries']={str(s):{k:float(np.mean([r[k] for r in result['rows'] if r['steps']==s])) for k in ('pairwise_ca_rmsd','peptide_outlier_fraction')} for s in c['steps']}
        result['sampling_seconds']={str(s):sum(r['seconds'] for r in m['batches'] if r['steps']==s) for s in c['steps']}
        result['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Teacher seed and integration-step diagnostic','',f"Status: {result['status']}.",'',result['scope'],'','Full-fold controls include the confidence head; production sampling timing excludes it. Thirty-two samples per target/setting, collected in fixed groups of eight.','', '| Steps | Mean pairwise CA RMSD (A) | Peptide outlier fraction | Structure sampling seconds |','|---|---:|---:|---:|']
    for s,r in result.get('summaries',{}).items():lines.append(f"| {s} | {r['pairwise_ca_rmsd']:.4f} | {r['peptide_outlier_fraction']:.4f} | {result['sampling_seconds'][s]:.2f} |")
    if 'error' in result:lines+=['',result['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
