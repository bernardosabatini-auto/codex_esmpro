"""Describe diversity of cached compatible states; does not authorize training."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from audit_fragment_teacher_targets import proper_rmsd_batch
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--inventory',type=Path,required=True);p.add_argument('--subset-fragments',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=json.loads(a.inventory.read_text())
    if d['status']!='complete':raise ValueError('Incomplete compatible-state inventory')
    with h5py.File(a.subset_fragments) as subset:ids=set(subset['train'])
    handles={};rows=[]
    try:
        for s in d['source_shards']:
            if sha(s['manifest'])!=s['manifest_sha256'] or sha(s['labels'])!=s['labels_sha256']:raise ValueError('Changed cached source')
        for r in d['records']:
            states=[x['index'] for x in r['eligible_states']];row={k:r[k] for k in ['target_id','condition','bucket','length']};row.update(in_subset=r['target_id'] in ids,eligible_states=len(states),pair_count=0,max_whole_rmsd=None,max_scaffold_rmsd=None,mean_scaffold_rmsd=None)
            if len(states)>=2:
                path=r['source_labels']
                if path not in handles:handles[path]=h5py.File(path)
                bb=handles[path][r['target_id']+'/teacher_backbone'][states,:,1,:];keep=np.ones(r['length'],bool);keep[r['motif_start']:r['motif_start']+r['motif_length']]=False;whole=[];scaffold=[]
                for i in range(len(states)-1):
                    whole.extend(proper_rmsd_batch(bb[i+1:],bb[i]).tolist());scaffold.extend(proper_rmsd_batch(bb[i+1:,keep],bb[i,keep]).tolist())
                row.update(pair_count=len(whole),max_whole_rmsd=max(whole),max_scaffold_rmsd=max(scaffold),mean_scaffold_rmsd=float(np.mean(scaffold)))
            rows.append(row)
        summaries={}
        for name,rr in [('all512',rows),('current128',[r for r in rows if r['in_subset']])]:
            multi=[r for r in rr if r['pair_count']];summaries[name]=dict(conditions=len(rr),eligible_conditions=sum(r['eligible_states']>0 for r in rr),multiple_state_conditions=len(multi),median_max_scaffold_rmsd=float(np.median([r['max_scaffold_rmsd'] for r in multi])) if multi else None,conditions_with_scaffold_pair_over_1A=sum(r['max_scaffold_rmsd']>1 for r in multi),proteins_with_scaffold_pair_over_1A=len({r['target_id'] for r in multi if r['max_scaffold_rmsd']>1}))
        out=dict(status='complete',inventory_sha256=sha(a.inventory),subset_fragments_sha256=sha(a.subset_fragments),summaries=summaries,records=rows,scope='Descriptive CPU-only diagnostic on training proteins. All pairs of states that passed unchanged original0.5Afragment and0.8confidence eligibility. Proper-RMSD metrics use fixed residue correspondence. The1Adiversity count is descriptive, not a qualification gate or designability measure. Original broad-coverage failure is unchanged; no target replacement or model training follows automatically.')
        a.output.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Diversity of compatible cached teacher states\n\n'+out['scope']+'\n\n```json\n'+json.dumps(summaries,indent=2)+'\n```\n');print(json.dumps(summaries))
    finally:
        for f in handles.values():f.close()


if __name__=='__main__':main()
