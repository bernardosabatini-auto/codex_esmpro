"""Report fixed-head conditioning training and paired native tuning metrics."""
import argparse,json
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0]
    m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest');result=dict(status=m['status'],scope=m.get('scope'),arm=m.get('config',{}).get('arm'),summaries={})
    if m['status']=='complete':
        if m['updates']!=500 or len(m['scores'])!=3*64*3 or len(m['controls'])!=8:raise ValueError('incomplete updates/evaluation/controls')
        grouped={}
        for step in (0,250,500):
            rows=[r for r in m['scores'] if r['step']==step];ids={r['target_id'] for r in rows}
            if len(ids)!=64 or any({r['sample'] for r in rows if r['target_id']==i}!={0,1,2} for i in ids):raise ValueError('incorrect evaluation coverage')
            grouped[step]={i:float(np.mean([r['ca_lddt'] for r in rows if r['target_id']==i])) for i in ids}
            result['summaries'][str(step)]=dict(mean_ca_lddt=float(np.mean(list(grouped[step].values()))),mean_ca_rmsd=float(np.mean([r['ca_rmsd'] for r in rows])))
        result['paired_diagnostics']={str(step):paired_comparison(grouped[step],grouped[0]) for step in (250,500)}
        result['training_seconds']=sum(r['seconds'] for r in m['batches']);result['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        try:result['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:result['hardware']=dict(status='unavailable',error=str(error))
    else:result['error']=m.get('error','Incomplete run')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Residual conditioning screen','',f"Status: {result['status']}; arm: {result['arm']}.",'',str(result['scope']),'','512 reference-supervised training families; 64 tuning families, three fixed sampling seeds. Source structures are inherited AFDB predictions. Flow head and ProteinAE decoder stay frozen. Layer confirmation and original independent test are not scored here.','', '| Updates | Mean CA lDDT | Mean CA RMSD (A) |','|---|---:|---:|']
    for step,r in result['summaries'].items():lines.append(f"| {step} | {r['mean_ca_lddt']:.5f} | {r['mean_ca_rmsd']:.3f} |")
    if 'error' in result:lines+=['',result['error']]
    lines+=['','This is a single training-seed tuning screen. Promotion requires replication and matched ensemble/accuracy checks.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
