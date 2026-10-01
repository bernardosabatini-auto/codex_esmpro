"""Report calibration reconstruction and paired decoder variability."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics,paired_comparison
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='No manifest')
    result=dict(status=m['status'],scope='16 mapped training structures; adapter calibration only',rows=[])
    if m['status']=='complete':
        if len(m['targets'])!=16 or len(m['batches'])!=64:raise ValueError('incomplete target/settings coverage')
        with h5py.File(run/'predictions.h5','r') as h:
            if set(h)!={str(i) for i in range(16)}:raise ValueError('incomplete prediction file')
            for key,g in h.items():
                ref=g['reference_backbone'][:,1]
                for latent in ('fresh','cached'):
                    for steps in (3,10):
                        pred=g[f'{latent}_steps{steps}'][:]
                        if pred.shape!=(8,len(ref),4,3):raise ValueError('invalid seed coverage')
                        metrics=[ca_metrics(x[:,1],ref) for x in pred]
                        pair_rmsd=[ca_metrics(pred[i,:,1],pred[j,:,1])['ca_rmsd'] for i in range(8) for j in range(i)]
                        peptide=np.linalg.norm(pred[:,:-1,2]-pred[:,1:,0],axis=-1)
                        result['rows'].append(dict(target_id=g.attrs['target_id'],latent=latent,steps=steps,ca_rmsd=float(np.mean([x['ca_rmsd'] for x in metrics])),ca_lddt=float(np.mean([x['ca_lddt'] for x in metrics])),pairwise_rmsd=float(np.mean(pair_rmsd)),peptide_outlier_fraction=float(np.mean((peptide<1.1)|(peptide>1.6)))))
        result['summaries']={f'{latent}_steps{steps}':{metric:float(np.mean([r[metric] for r in result['rows'] if r['latent']==latent and r['steps']==steps])) for metric in ('ca_rmsd','ca_lddt','pairwise_rmsd','peptide_outlier_fraction')} for latent in ('fresh','cached') for steps in (3,10)}
        result['fresh_step_effect']={metric:paired_comparison({r['target_id']:r[metric] for r in result['rows'] if r['latent']=='fresh' and r['steps']==3},{r['target_id']:r[metric] for r in result['rows'] if r['latent']=='fresh' and r['steps']==10}) for metric in ('ca_lddt','pairwise_rmsd')}
        result['latent_rmse_mean']=float(np.mean([r['latent_rmse'] for r in m['targets']]))
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','Incomplete calibration')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# ProteinAE round-trip calibration','',f"Status: {result['status']}.",'','16 mapped training structures, eight paired decoder seeds, strict FP32. This validates reconstruction and decoder variability; it does not measure experimental ensemble coverage. CA coordinates and distances are in Angstrom.','', '| Latent / decoder steps | Mean CA RMSD | Mean CA lDDT | Mean pairwise RMSD | Peptide outlier fraction |','|---|---:|---:|---:|---:|']
    for key,r in result.get('summaries',{}).items():lines.append(f"| {key} | {r['ca_rmsd']:.4f} | {r['ca_lddt']:.4f} | {r['pairwise_rmsd']:.4f} | {r['peptide_outlier_fraction']:.4f} |")
    if 'error' in result:lines+=['',result['error']]
    lines+=['','Independent-test targets were not used. Seed dispersion alone is not evidence of useful conformational diversity.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
