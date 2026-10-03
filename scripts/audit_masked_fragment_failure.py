"""Post hoc localization of failed inpainting geometry; no gate changes."""
import argparse,json
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.masked_fragment_flow import editable_window
from latentfold.ensemble_metrics import backbone_geometry
from extra_fragment_validation_core import load_conditions
from prepare_overfit import sha


def analyze(run,report):
    m=json.loads((run/'manifest.json').read_text());d=json.loads(report.read_text());c=m['config']
    if (m['status']!='complete' or d['status']!='complete' or d['profile_only'] or d['refold_gate']['qualified']
        or d['manifest_sha256']!=sha(run/'manifest.json') or d['predictions_sha256']!=sha(run/'predictions.h5')):raise ValueError('Expected audited failed full repair experiment')
    items=load_conditions(c['fragments'],[r['id'] for r in c['selected']],'c20_center',cohort='train');records=[]
    with h5py.File(run/'predictions.h5') as f:
        for arm in ('parent','native_direct','generated_cond','generated_null','native_cond','native_null'):
            for source in c['selected']:
                ident=source['id'];item=items[ident];n=item['length'];edit=editable_window(item['keep'][None],torch.ones(1,n,dtype=torch.bool),c['spec']['flank'])[0].numpy()
                inside=edit[:-1]&edit[1:];boundary=edit[:-1]^edit[1:];outside=~edit[:-1]&~edit[1:]
                bb=f[arm+'/'+ident+'/backbone'][:];z=f[arm+'/'+ident+'/latent'][:];native=f['native_direct/'+ident+'/latent'][:];geometry=backbone_geometry(bb)
                peptide=np.linalg.norm(bb[:,:-1,2]-bb[:,1:,0],axis=-1);peptide_bad=(peptide<1.1)|(peptide>1.6);gaps=np.linalg.norm(np.diff(bb[:,:,1],axis=1),axis=-1)>4.5
                distance=np.linalg.norm(bb[:,:,None,1]-bb[:,None,:,1],axis=-1);index=np.arange(n);pairs=np.triu(np.abs(index[:,None]-index[None,:])>2,1);clashes=(distance<2.5)&pairs
                for slot in range(4):
                    recorded=next(r for r in d['records'] if (r['arm'],r['target_id'],r['generation_slot'])==(arm,ident,slot))
                    if bool(geometry['coarse_valid'][slot])!=recorded['coarse_valid']:raise ValueError('Changed geometry scoring')
                    row=dict(arm=arm,target_id=ident,slot=slot,bucket=source['bucket'],motif_fit_without_geometry=recorded['motif_ca_rmsd']<=1 and recorded['motif_drms']<=1,
                             peptide_failure=bool(geometry['peptide_outlier_fraction'][slot]>.05),clash_failure=bool(geometry['ca_clashing_residue_fraction'][slot]>.01),gap_failure=bool(geometry['ca_gap_fraction'][slot]>.01))
                    for region,selection in [('editable',inside),('boundary',boundary),('fixed',outside)]:
                        row[region+'_peptide_outliers']=int(peptide_bad[slot,selection].sum());row[region+'_ca_gaps']=int(gaps[slot,selection].sum())
                    row['clashes_touching_editable']=int((clashes[slot]&(edit[:,None]|edit[None,:])).sum());row['clashes_fixed_only']=int((clashes[slot]&(~edit[:,None]&~edit[None,:])).sum())
                    if arm.startswith('native'):row['editable_latent_mse_to_native']=float(np.mean((z[slot,edit]-native[slot,edit])**2))
                    records.append(row)
    summary=[]
    for arm in ('parent','native_direct','generated_cond','generated_null','native_cond','native_null'):
        rr=[r for r in records if r['arm']==arm];keys=[k for k in rr[0] if k not in ('arm','target_id','slot','bucket','editable_latent_mse_to_native')];row=dict(arm=arm,samples=len(rr),**{k:sum(r[k] for r in rr) for k in keys})
        if 'editable_latent_mse_to_native' in rr[0]:row['mean_editable_latent_mse_to_native']=float(np.mean([r['editable_latent_mse_to_native'] for r in rr]))
        summary.append(row)
    return dict(status='complete',source_report_sha256=sha(report),manifest_sha256=sha(run/'manifest.json'),summary=summary,records=records,scope='Post hoc failure localization on the same training diagnostic. Bond/clash/gap failure categories overlap. Link/pair counts are totals over128 samples, not independent observations. No altered gate or new labels; native-context error is an oracle capacity measure, not generated-structure accuracy.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.run,a.report);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Learned inpainting failure localization\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n');print(json.dumps(d['summary']))


if __name__=='__main__':main()
