"""Report noise-source dispersion and basic backbone geometry; no coverage claim."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from summarize_comparison import hardware


def rmsd(x,y):
    x=x.astype(float)-x.mean(0);y=y.astype(float)-y.mean(0);u,_,v=np.linalg.svd(x.T@y)
    rotation=u@np.diag([1,1,np.linalg.det(u@v)])@v
    return float(np.sqrt(np.mean(np.sum((x@rotation-y)**2,axis=-1))))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='No manifest')
    result=dict(status=m['status'],rows=[],scope='Noise-source diagnostic; dispersion is not useful state coverage. Peptide outliers are one geometry check, not a complete physical-validity assessment. Shared seeds across arms are paired repeated measurements.')
    if m['status']=='complete':
        path=Path(m['config']['panel'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=m['config']['panel_sha256']:raise ValueError('changed frozen panel')
        rows={r['query_id']:r for r in json.loads(path.read_text())['development']}
        if len(m['targets'])!=48 or len(m['controls'])!=56:raise ValueError('incomplete predictions/controls')
        with h5py.File(run/'predictions.h5') as h:
            if set(h)!=set(rows):raise ValueError('incorrect target coverage')
            for ident,g in h.items():
                expected={'cfg2','cfg1'} if ident in m['config']['guidance_controls'] else {'cfg2'}
                if set(g)!=expected:raise ValueError('missing guidance arm')
                for cfg,cg in g.items():
                    if set(cg)!={'z','latent','decoder','factorial'}:raise ValueError('missing noise arm')
                    for arm in ('latent','decoder','factorial'):
                        bb=cg[arm]['backbone'][:]
                        if bb.shape!=(32,rows[ident]['length'],4,3) or not np.isfinite(bb).all():raise ValueError('invalid sample coverage')
                        ca=bb[:,:,1];pairs=[rmsd(ca[i],ca[j]) for i in range(32) for j in range(i)]
                        peptide=np.linalg.norm(bb[:,:-1,2]-bb[:,1:,0],axis=-1);outlier=(peptide<1.1)|(peptide>1.6)
                        result['rows'].append(dict(target_id=ident,category=rows[ident]['category'],guidance=cfg,arm=arm,pairwise_ca_rmsd=float(np.mean(pairs)),peptide_outlier_fraction=float(outlier.mean()),sample_outlier_fraction_p90=float(np.quantile(outlier.mean(1),.9))))
        result['summaries']={arm:{key:float(np.mean([r[key] for r in result['rows'] if r['guidance']=='cfg2' and r['arm']==arm])) for key in ('pairwise_ca_rmsd','peptide_outlier_fraction')} for arm in ('latent','decoder','factorial')}
        result['stage_seconds']={stage:sum(r['seconds'] for r in m['batches'] if r['stage']==stage) for stage in ('embedding','latent','decoder')}
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Sequence-conditioned ensemble diagnostic','',f"Status: {result['status']}.",'',result['scope'],'','48 frozen development proteins; 32 samples per noise arm; CFG 2, plus CFG 1 on eight preselected proteins. Strict FP32, 25 latent-flow steps and three decoder steps. Confirmation targets remain unscored.','', '| Noise arm | Mean pairwise CA RMSD (A) | Peptide outlier fraction |','|---|---:|---:|']
    for arm,row in result.get('summaries',{}).items():lines.append(f"| {arm} | {row['pairwise_ca_rmsd']:.4f} | {row['peptide_outlier_fraction']:.4f} |")
    if 'error' in result:lines+=['',result['error']]
    lines+=['','Reference-state and MD-distribution evaluations are separate; this report alone cannot justify teacher distillation or model promotion.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
