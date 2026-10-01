"""Report paired structure accuracy and utilization of ensemble-label training."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest')
    c=m.get('config',{});d=dict(status=m['status'],arm=c.get('arm'),profile_only=c.get('profile_only',False),summaries={})
    if m['status']=='complete':
        if m['updates']!=c['updates']:raise ValueError('incomplete training')
        if not c.get('profile_only'):
            steps=[0]+c['evaluation_steps'];grouped={}
            if len(m['scores'])!=len(steps)*64*3 or len(m['controls'])!=4:raise ValueError('incomplete evaluation')
            for step in steps:
                rows=[r for r in m['scores'] if r['step']==step];ids={r['target_id'] for r in rows}
                if len(ids)!=64 or any({r['sample'] for r in rows if r['target_id']==i}!={0,1,2} for i in ids):raise ValueError('evaluation coverage mismatch')
                grouped[step]={i:float(np.mean([r['ca_lddt'] for r in rows if r['target_id']==i])) for i in ids}
                d['summaries'][str(step)]={key:float(np.mean([r[key] for r in rows])) for key in ('ca_lddt','ca_rmsd','tm_after_kabsch','coarse_valid','peptide_outlier_fraction','ca_clashing_residue_fraction')}
            d['paired_diagnostics']={str(step):paired_comparison(grouped[step],grouped[0]) for step in steps[1:]}
        d['training_seconds']=sum(r['seconds'] for r in m['batches']);d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Ensemble-label training','',f"Status: {d['status']}; arm: {d['arm']}; capacity profile only: {d['profile_only']}.",'','AFDB predicted references and ESMFold2 predicted ensembles. Full flow head trained; ProteinAE and ESMC frozen. Raw-reference and canonical-reference controls isolate pose preprocessing. Empirical and cluster-balanced arms draw 50% reference and 50% valid teacher labels; no valid teacher implies reference fallback. Clusters are not measured state populations.','', '| Updates | Mean CA lDDT | CA RMSD (A) | TM after Kabsch | Coarse valid |','|---|---:|---:|---:|---:|']
    for step,r in d['summaries'].items():lines.append(f"| {step} | {r['ca_lddt']:.5f} | {r['ca_rmsd']:.3f} | {r['tm_after_kabsch']:.5f} | {r['coarse_valid']:.5f} |")
    if 'error' in d:lines+=['',d['error']]
    lines+=['','Tuning results alone do not establish ensemble improvement. Evaluate frozen development state coverage and coarse validity, then replicate eligible effects. Confirmation and original test remain quarantined.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
