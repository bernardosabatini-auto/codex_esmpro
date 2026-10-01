"""Summarize matched representation probes without a generative accuracy claim."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest');result=dict(status=m['status'],scope=m.get('scope'),summaries={})
    if m['status']=='complete':
        if len(m['controls'])!=16 or len(m['scores'])!=4*len(m['config']['ridge'])*64:raise ValueError('incomplete probe controls/scores')
        for layer in (20,40,60,80):
            for ridge in m['config']['ridge']:
                rows=[r for r in m['scores'] if r['layer']==layer and r['ridge']==ridge]
                if len({r['target_id'] for r in rows})!=64:raise ValueError('probe target mismatch')
                result['summaries'][f'{layer}/{ridge}']=dict(layer=layer,ridge=ridge,ca_lddt=float(np.mean([r['ca_lddt'] for r in rows])),ca_rmsd=float(np.mean([r['ca_rmsd'] for r in rows])),latent_mse=float(np.mean([r['latent_mse'] for r in rows])))
        best={layer:max([r for r in result['summaries'].values() if r['layer']==layer],key=lambda r:r['ca_lddt']) for layer in (20,40,60,80)};result['best_per_layer_on_tuning']=best
        baseline={r['target_id']:r['ca_lddt'] for r in m['scores'] if r['layer']==80 and r['ridge']==best[80]['ridge']}
        result['paired_tuning_diagnostics']={str(layer):paired_comparison({r['target_id']:r['ca_lddt'] for r in m['scores'] if r['layer']==layer and r['ridge']==best[layer]['ridge']},baseline) for layer in (20,40,60)}
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','Incomplete probe')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Matched ESMC layer probes','',f"Status: {result['status']}.",'',str(result['scope']),'','| Layer | Ridge | Tuning CA lDDT | Tuning CA RMSD | Latent MSE |','|---|---:|---:|---:|---:|']
    for r in result['summaries'].values():lines.append(f"| {r['layer']} | {r['ridge']} | {r['ca_lddt']:.4f} | {r['ca_rmsd']:.3f} | {r['latent_mse']:.4f} |")
    lines+=['','Ridge selection and paired differences use the tuning set, so they cannot establish confirmation or a generative-model improvement. Learned mixtures and full flow training require separate matched tests.']
    if 'error' in result:lines+=['',result['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
