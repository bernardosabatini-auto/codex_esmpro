"""Post-hoc scaffold agreement on prospectively selected first successful refolds."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates,ca_metrics
from latentfold.fragment_designability import scaffold_rmsd
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--all-refolds',action='store_true');a=p.parse_args()
    d=json.loads(a.report.read_text());m=json.loads((a.run/'manifest.json').read_text());c=m['config']
    if d['status']!='complete' or d['manifest_sha256']!=sha(a.run/'manifest.json') or d['refolded_sha256']!=sha(a.run/'refolded.h5') or c['predictions_sha256']!=sha(c['predictions']):raise ValueError('Changed audited assay')
    rows=[]
    with h5py.File(c['predictions']) as raw,h5py.File(a.run/'refolded.h5') as folds:
        for r in d['records']:
            if not a.all_refolds and (r['arm']=='native' or not r['strict_joint_success']):continue
            for k in (range(8) if a.all_refolds else [r['successful_refold_indices'][0]]):
                x=raw[r['dataset']][0];y=folds[r['name']+'/'+str(k)][:];keep=np.zeros(len(x),dtype=bool);start=r['motif_start'];keep[start:start+len(raw['motifs/'+r['target_id']])]=True
                reference=r['refolds'][k]
                if abs(usalign_coordinates(c['usalign'],y[:,1],x[:,1])-reference['sc_tm'])>1e-7:raise ValueError('Changed primary score')
                tm=usalign_coordinates(c['usalign'],y[~keep,1],x[~keep,1]);primary=r['raw_gate_passed'] and k in r['successful_refold_indices']
                rows.append(dict(arm=r['arm'],target_id=r['target_id'],generation_slot=r['generation_slot'],sequence_index=k,motif_residues=int(keep.sum()),scaffold_residues=int((~keep).sum()),primary_joint_success=primary,scaffold_joint_success=primary and tm>.5,global_tm=reference['sc_tm'],scaffold_only_tm=tm,scaffold_only_lddt=ca_metrics(y[~keep,1],x[~keep,1])['ca_lddt'],motif_aligned_scaffold_rmsd=scaffold_rmsd(y,x,keep)))
    counts={arm:len({(r['target_id'],r['generation_slot']) for r in rows if r['arm']==arm and r['scaffold_joint_success']}) for arm in sorted({r['arm'] for r in rows})}
    result=dict(status='complete',all_refolds=a.all_refolds,scaffold_joint_backbones=counts,source_report_sha256=sha(a.report),rows=rows,scope='Post-hoc diagnostic with fixed residue correspondence. Default uses first qualifying refolds; --all-refolds audits the complete eight-design budget and positive controls. Supplementary scaffold joint success adds scaffold-only TM>0.5 in the SAME qualifying refold, with raw failures retained. Scaffold-only TM excludes all supplied motif residues and normalizes by scaffold length. It does not alter the preregistered strict outcome or select replacement refolds. Motif-aligned scaffold RMSD measures relative placement, including flexible deviations.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Agreement outside the supplied fragment','',result['scope'],'','Supplementary scaffold joint backbones: '+json.dumps(counts), '', '| Arm | Target / slot / sequence | Global TM | Scaffold-only TM | Scaffold lDDT | Motif-aligned scaffold RMSD |','|---|---|---:|---:|---:|---:|']
    for r in rows:lines.append(f"| {r['arm']} | {r['target_id']} / {r['generation_slot']} / {r['sequence_index']} | {r['global_tm']:.3f} | {r['scaffold_only_tm']:.3f} | {r['scaffold_only_lddt']:.3f} | {r['motif_aligned_scaffold_rmsd']:.2f} Å |")
    lines+=['',f"Source report SHA256: `{result['source_report_sha256']}`."]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(scored_refolds=len(rows),scaffold_joint_backbones=counts)))


if __name__=='__main__':main()
