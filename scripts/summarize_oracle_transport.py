import argparse,json
from pathlib import Path
import numpy as np
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'],summaries={})
    if m['status']=='complete':
        if len(m['scores'])!=256 or len(m['controls'])!=8:raise ValueError('incomplete control')
        for arm in ('aligned','pca'):
            for steps in (5,10,25,100):
                rows=[r for r in m['scores'] if r['arm']==arm and r['steps']==steps]
                if len(rows)!=32 or len({r['target_id'] for r in rows})!=32:raise ValueError('incomplete target coverage')
                d['summaries'][f'{arm}_{steps}']=dict(coverage32=float(np.mean([r['coverage']['32'] for r in rows])),strict_coverage32=float(np.mean([r['strict_coverage']['32'] for r in rows])),**{k:float(np.mean([r[k] for r in rows])) for k in ('valid_fraction','teacher_ca_lddt','state_total_variation','teacher_sampling_expected_coverage32')})
        d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as e:d['hardware']=dict(status='unavailable',error=str(e))
    else:d['error']=m.get('error','Incomplete oracle control')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Oracle flow and decoder positive control','',f"Status: {d['status']}.",'','This vector field knows the complete empirical teacher latent distribution for each training protein. It is not deployable prediction and cannot establish learned-model accuracy. Same fresh32 Gaussian seeds and decoder seeds as the capacity test; ordinary Euler integration, latent layer normalization and3-step decoding.','', '| Frame / steps | Recall @2A | Recall @1A | Coarse valid | Teacher CA-lDDT | State TV | Ideal teacher recall @32 |','|---|---:|---:|---:|---:|---:|---:|']
    for key,r in d['summaries'].items():lines.append(f"| {key} | {r['coverage32']:.5f} | {r['strict_coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['state_total_variation']:.5f} | {r['teacher_sampling_expected_coverage32']:.5f} |")
    if 'error' in d:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
