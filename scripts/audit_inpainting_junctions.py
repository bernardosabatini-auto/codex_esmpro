"""Secondary continuity diagnostic; never replaces the fixed primary assay.

The coarse whole-chain validity score tolerates a small fraction of bad bonds.
Check both fragment/scaffold junctions in each SAME qualifying refold as well.
"""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha
from compare_native_anchor_models import verify_outcome


def junctions(bb,start,length):
    if (bb.ndim!=3 or bb.shape[1:]!=(4,3) or not np.isfinite(bb).all()
            or start<0 or length<1 or start+length>len(bb)):
        raise ValueError('Finite backbone and contained motif required')
    edges=[i for i in (start-1,start+length-1) if 0<=i<len(bb)-1]
    if not edges:raise ValueError('A scaffold junction is required')
    cn=np.array([np.linalg.norm(bb[i,2]-bb[i+1,0]) for i in edges])
    ca=np.array([np.linalg.norm(bb[i,1]-bb[i+1,1]) for i in edges])
    return dict(edges=edges,peptide_distances=cn.tolist(),ca_distances=ca.tolist(),
                valid=bool(((cn>=1.1)&(cn<=1.6)&(ca<=4.5)).all()))


def analyze(comparison):
    d=json.loads(comparison.read_text())
    if d['status']!='complete':raise ValueError('Complete primary comparison required')
    records=[]
    for source in d['source_reports']:
        path=Path(source['path'])
        if sha(path)!=source['sha256']:raise ValueError('Changed primary source report')
        r=json.loads(path.read_text());run=path.parents[1]/'runs'/path.stem
        if r['manifest_sha256']!=sha(run/'manifest.json') or r['refolded_sha256']!=sha(run/'refolded.h5'):
            raise ValueError('Changed refold evidence')
        config=json.loads((run/'manifest.json').read_text())['config']
        if sha(config['predictions'])!=config['predictions_sha256']:raise ValueError('Changed raw backbones')
        with h5py.File(config['predictions']) as raw,h5py.File(run/'refolded.h5') as folded:
            for row in r['records']:
                verify_outcome(row)
                initial=junctions(raw[row['dataset']][0],row['motif_start'],len(row['fixed_sequence']))
                qualifying=[dict(sequence_index=k,**junctions(folded[row['name']+'/'+str(k)][:],row['motif_start'],len(row['fixed_sequence'])))
                            for k in row['scaffold_successful_refold_indices']]
                records.append(dict(arm=row['arm'],target_id=row['target_id'],slot=row['generation_slot'],
                    raw_junction=initial,strict=row['scaffold_joint_success'],qualifying_refolds=qualifying,
                    strict_with_refold_junctions=any(x['valid'] for x in qualifying),
                    strict_with_both_junctions=initial['valid'] and any(x['valid'] for x in qualifying)))
    arms={r['arm'] for r in records}
    if arms!={'parent6000','generated_cond','generated_untrained'}:raise ValueError('Expected matched inpainting comparison')
    summary=[]
    for arm in sorted(arms):
        rr=[r for r in records if r['arm']==arm]
        if len(rr)!=128 or len({(r['target_id'],r['slot']) for r in rr})!=128:raise ValueError('Changed denominator')
        summary.append(dict(arm=arm,samples=128,raw_junctions_valid=sum(r['raw_junction']['valid'] for r in rr),
            **{k:sum(r[k] for r in rr) for k in ('strict','strict_with_refold_junctions','strict_with_both_junctions')}))
    return dict(status='complete',comparison_sha256=sha(comparison),summary=summary,records=records,
                scope='Secondary diagnostic specified after the40-update profile exposed boundary failures, before the full endpoint or new refolds. Primary criteria and all denominators remain unchanged. Require C-N1.1–1.6A and CA<=4.5A at both available junctions; both checks must hold in the SAME already-qualifying refold. This is backbone continuity, not a full chemical-validity assay.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(a.comparison);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    a.output.with_suffix('.md').write_text('# Inpainting junction continuity\n\n'+d['scope']+'\n\n```json\n'+json.dumps(d['summary'],indent=2)+'\n```\n')
    print(json.dumps(d['summary']))


if __name__=='__main__':main()
