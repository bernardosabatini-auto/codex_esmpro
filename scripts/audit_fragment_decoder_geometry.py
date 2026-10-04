"""Describe decoder geometry and learning without selecting samples or checkpoints."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np

from extra_fragment_validation_core import load_conditions
from latentfold.ensemble_metrics import backbone_geometry
from fragment_decoder_training_core import panel, refold_eligibility
from prepare_overfit import sha


def analyze(run, report):
    m=json.loads((run/'manifest.json').read_text()); d=json.loads(report.read_text()); c=m['config']
    if (m['status']!='complete' or d['status']!='complete' or not (d.get('fragment_decoder') or d.get('fragment_decoder_fm') or d.get('fragment_inpainting'))
            or not d['numerically_qualified'] or d['manifest_sha256']!=sha(run/'manifest.json')
            or d['predictions_sha256']!=sha(run/'predictions.h5')):
        raise ValueError('Complete audited decoder experiment required')
    selected=panel(c); ids=[r['id'] for r in selected]
    eligibility_function=refold_eligibility
    if d.get('fragment_inpainting'):
        from fragment_inpainting_core import refold_eligibility as eligibility_function
    if not c['profile_only']:
        gate=eligibility_function(d['summary'],d['records'],ids,c['spec'])
        if gate!=d['refold_eligibility']: raise ValueError('Changed eligibility')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train')
    lookup={(r['arm'],r['target_id'],r['generation_slot']):r for r in d['records']}
    arms=('parent','native_direct','generated_cond','generated_null','native_cond','native_null')
    if d.get('fragment_inpainting'):arms+=('generated_untrained','native_untrained')
    records=[]
    with h5py.File(run/'predictions.h5') as f:
        for arm in arms:
            for source in selected:
                ident=source['id']; keep=items[ident]['keep'].numpy(); n=len(keep)
                inside=keep[:-1]&keep[1:]; boundary=keep[:-1]^keep[1:]; outside=~keep[:-1]&~keep[1:]
                bb=f[arm+'/'+ident+'/backbone'][:]; geometry=backbone_geometry(bb)
                peptide=np.linalg.norm(bb[:,:-1,2]-bb[:,1:,0],axis=-1); bad=(peptide<1.1)|(peptide>1.6)
                gaps=np.linalg.norm(np.diff(bb[:,:,1],axis=1),axis=-1)>4.5
                distance=np.linalg.norm(bb[:,:,None,1]-bb[:,None,:,1],axis=-1)
                index=np.arange(n); pairs=np.triu(np.abs(index[:,None]-index[None,:])>2,1); clashes=(distance<2.5)&pairs
                for slot in range(4):
                    r=lookup[arm,ident,slot]
                    if bool(geometry['coarse_valid'][slot])!=r['coarse_valid']: raise ValueError('Geometry scoring changed')
                    row=dict(arm=arm,target_id=ident,slot=slot,bucket=source['bucket'],
                        motif_fit_without_geometry=r['motif_ca_rmsd']<=1 and r['motif_drms']<=1,
                        peptide_failure=bool(geometry['peptide_outlier_fraction'][slot]>.05),
                        clash_failure=bool(geometry['ca_clashing_residue_fraction'][slot]>.01),
                        gap_failure=bool(geometry['ca_gap_fraction'][slot]>.01))
                    for name,mask in [('motif',inside),('boundary',boundary),('scaffold',outside)]:
                        row[name+'_peptide_outliers']=int(bad[slot,mask].sum()); row[name+'_ca_gaps']=int(gaps[slot,mask].sum())
                    row['clashes_touching_motif']=int((clashes[slot]&(keep[:,None]|keep[None,:])).sum())
                    row['clashes_scaffold_only']=int((clashes[slot]&(~keep[:,None]&~keep[None,:])).sum())
                    records.append(row)
    summary=[]
    for arm in arms:
        rr=[r for r in records if r['arm']==arm]; keys=set(rr[0])-{'arm','target_id','slot','bucket'}
        summary.append(dict(arm=arm,samples=len(rr),**{k:sum(r[k] for r in rr) for k in sorted(keys)}))
    keys=[(i,k) for i in ids for k in range(4)]
    transitions=dict(retained_raw=sum(lookup['parent',i,k]['raw_gate_passed'] and lookup['generated_cond',i,k]['raw_gate_passed'] for i,k in keys),
        lost_raw=sum(lookup['parent',i,k]['raw_gate_passed'] and not lookup['generated_cond',i,k]['raw_gate_passed'] for i,k in keys),
        new_raw=sum(not lookup['parent',i,k]['raw_gate_passed'] and lookup['generated_cond',i,k]['raw_gate_passed'] for i,k in keys))
    learning=[]
    learning_keys=('loss','unknown_fm','gradient_norm') if d.get('fragment_inpainting') else ('loss','motif_fm','scaffold_fm','gradient_norm') if d.get('fragment_decoder_fm') else ('loss','position_mse','bond_mse','gradient_norm')
    for start in range(0,len(m['training']),200):
        for bucket in (128,256,384,512):
            rr=[r for r in m['training'][start:start+200] if r['bucket']==bucket]
            if rr: learning.append(dict(first_update=start+1,last_update=min(start+200,len(m['training'])),bucket=bucket,updates=len(rr),
                **{k:float(np.mean([r[k] for r in rr])) for k in learning_keys}))
    return dict(status='complete',profile_only=c['profile_only'],manifest_sha256=sha(run/'manifest.json'),
        source_report_sha256=sha(report),summary=summary,transitions=transitions,learning=learning,records=records,
        scope='Post hoc description of every output, with unchanged eligibility and no checkpoint selection. '+
        ('Regions refer to supplied20residue motif and its complement. Motif atoms are fixed in conditioned/untrained inpainting, and free in null controls. '
         if d.get('fragment_inpainting') else 'Regions refer to supplied20residue motif and its complement; all decoded atoms are free. ')+
        'Latent arrays are masked INPUTS, so no latent reconstruction accuracy is claimed. '
        'Bond/clash/gap categories overlap. Learning windows draw different proteins, not paired validation. '
        'Geometry cannot establish designability; only the same-valid-refold assay can.')


def main():
    p=argparse.ArgumentParser(); p.add_argument('--run',type=Path,required=True); p.add_argument('--report',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    d=analyze(a.run,a.report); a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    visible={k:v for k,v in d.items() if k not in ('records','learning')}
    a.output.with_suffix('.md').write_text('# Decoder-conditioning geometry diagnosis\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n')
    print(json.dumps(dict(transitions=d['transitions'],summary=d['summary'])))


if __name__=='__main__': main()
