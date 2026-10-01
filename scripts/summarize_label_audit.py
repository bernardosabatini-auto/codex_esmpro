import argparse,json
from pathlib import Path
import numpy as np
from summarize_comparison import hardware


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];m=json.loads((run/'manifest.json').read_text()) if (run/'manifest.json').exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'],training_gate_passed=False,label_shards=m.get('config',{}).get('label_shards'))
    if m['status']=='complete':
        rows=m['rows']
        if len(rows)!=512 or len(m['controls'])!=4:raise ValueError('incomplete audit')
        d.update(mean_ca_lddt=float(np.mean([r['mean_ca_lddt'] for r in rows])),min_ca_lddt=min(r['min_ca_lddt'] for r in rows),mean_ca_rmsd=float(np.mean([r['mean_ca_rmsd'] for r in rows])),input_valid_fraction=sum(r['input_valid'] for r in rows)/8192,decoded_valid_fraction=sum(r['decoded_valid'] for r in rows)/8192)
        d['training_gate_passed']=d['mean_ca_lddt']>=.98 and d['decoded_valid_fraction']>=d['input_valid_fraction']-.01
        try:d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete audit')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Full teacher-latent reconstruction audit','',f"Status: {d['status']}; training gate passed: {d['training_gate_passed']}.",'','All8,192 teacher conformations across512 training families, three ProteinAE decoder steps, fixed decoder noise within each protein. GPU metrics checked against CPU references in all four length buckets. Thresholds: mean CA lDDT at least0.98, decoded coarse validity no more than0.01 below input validity.']
    for key in ('mean_ca_lddt','min_ca_lddt','mean_ca_rmsd','input_valid_fraction','decoded_valid_fraction','error'):
        if key in d:lines+=['',f'{key}: {d[key]}']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
