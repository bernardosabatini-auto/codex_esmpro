"""Score frozen ensembles against reference-selected state and MD features."""
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np
from latentfold.ensemble_metrics import backbone_geometry,project_md,sliced_wasserstein_2d
from latentfold.metrics import ca_metrics
from summarize_ensemble import rmsd


def state_definition(row):
    positions=row['common_indices'];refs=[np.asarray(r['backbone'])[[r['observed_indices'].index(i) for i in positions],1] for r in row['references']]
    matrices=np.stack([np.linalg.norm(x[:,None]-x[None,:],axis=-1) for x in refs]);i,j=np.triu_indices(len(positions),k=1)
    keep=(np.abs(np.asarray(positions)[i]-np.asarray(positions)[j])>3)&(np.ptp(matrices[:,i,j],axis=0)>=2)&(matrices[:,i,j].min(0)<=12)
    i,j=i[keep],j[keep];features=matrices[:,i,j];parent=list(range(len(refs)))
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    if len(i):
        for a in range(len(refs)):
            for b in range(a):
                if np.sqrt(np.mean((features[a]-features[b])**2))<=1:parent[find(a)]=find(b)
    labels=[find(k) for k in range(len(refs))]
    return positions,refs,i,j,features,labels


def main():
    p=argparse.ArgumentParser()
    for name in ('run','assets','protocol','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();m=json.loads((a.run/'manifest.json').read_text());c=m['config']
    if m['status']!='complete' or m.get('teacher_adapter',{}).get('loading',{}).get('mismatched_keys'):raise ValueError('run is not eligible')
    panel=Path(c['panel'])
    if hashlib.sha256(panel.read_bytes()).hexdigest()!=c['panel_sha256']:raise ValueError('panel changed')
    rows={r['query_id']:r for r in json.loads(panel.read_text())['development']};teacher='target_ids' in c
    if teacher and not m.get('teacher_adapter'):raise ValueError('teacher lacks guarded corrected adapter')
    protocol=json.loads(a.protocol.read_text());result=dict(status='running',run=str(a.run.resolve()),protocol=protocol,protocol_sha256=hashlib.sha256(a.protocol.read_bytes()).hexdigest(),rows=[],definitions={},scope='Development contact-state coverage and MD distributions; no independent-generalization claim')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    md=a.assets/'bioemu_benchmarks/assets/md_emulation_benchmark_0.1/md_emulation'
    with np.load(md/'projections_mean.npz') as means,np.load(md/'projections_sqrt_inv_cov.npz') as transforms,np.load(md/'reference_projections.npz') as references,h5py.File(a.run/'predictions.h5') as h:
        for ident,g in h.items():
            row=rows[ident];category='md' if row['category']=='md_emulation' else 'control' if row['category']=='nmr_control' else 'multistate'
            if category!='md':
                positions,refs,i,j,ref_features,labels=state_definition(row)
                result['definitions'][ident]=dict(variable_contacts=len(i),reference_states=len(set(labels)) if len(i) else 0,reference_cluster_labels=labels)
            else:
                key=row['id'];reference=references[key];result['definitions'][ident]=dict(reference_samples=len(reference),projection_dimensions=reference.shape[-1])
            settings=[(setting,g[setting]['backbone'][:]) for setting in g] if teacher else [(cfg+'/'+arm,g[cfg][arm]['backbone'][:]) for cfg in g for arm in ('latent','decoder','factorial')]
            for setting,bb in settings:
                if bb.shape!=(32,row['length'],4,3):raise ValueError('unexpected ensemble size')
                geometry=backbone_geometry(bb);entry=dict(target_id=ident,family=row['family'],category=category,setting=setting,coarse_valid_fraction=float(geometry['coarse_valid'].mean()),mean_peptide_outlier_fraction=float(geometry['peptide_outlier_fraction'].mean()))
                if category=='md':
                    projection=project_md(bb[:,:,1],means[key],transforms[key]);entry['projection_wasserstein']={str(k):sliced_wasserstein_2d(projection[:k],reference) for k in (1,4,16,32)}
                else:
                    ca=bb[:,positions,1];quality=np.array([[ca_metrics(x,y)['ca_lddt'] for y in refs] for x in ca]);entry['oracle_nearest_reference_ca_lddt_mean']=float(quality.max(1).mean())
                    if category=='multistate' and len(i) and len(set(labels))>1:
                        features=np.linalg.norm(ca[:,i]-ca[:,j],axis=-1);errors=np.sqrt(np.mean((features[:,None,:]-ref_features[None,:,:])**2,axis=-1));nearest=errors.argmin(1);best=errors[np.arange(32),nearest]
                        entry['contact_state_count']=len(set(labels));entry['coverage']={}
                        for threshold in (1.,2.,3.):
                            good=(best<=threshold)&(quality.max(1)>=.8)&geometry['coarse_valid'];assignments=[labels[n] if ok else None for n,ok in zip(nearest,good)]
                            entry['coverage'][str(threshold)]={str(k):len({x for x in assignments[:k] if x is not None})/len(set(labels)) for k in (1,4,16,32)}
                        entry['minimum_feature_rmse']=float(best.min());entry['mean_feature_rmse']=float(best.mean())
                    elif category=='multistate':entry['coverage_exclusion']='Fewer than two reference-distinguishable contact states'
                    else:
                        entry['generated_pairwise_rmsd']=float(np.mean([rmsd(ca[x],ca[y]) for x in range(32) for y in range(x)]));entry['reference_pairwise_rmsd']=row['mean_pairwise_ca_rmsd']
                result['rows'].append(entry)
            print('scored',ident,flush=True)
    result['status']='complete';result['summaries']={}
    for setting in sorted({r['setting'] for r in result['rows']}):
        selected=[r for r in result['rows'] if r['setting']==setting];multi=[r for r in selected if 'coverage' in r];mdrows=[r for r in selected if r['category']=='md'];qualities=[r['oracle_nearest_reference_ca_lddt_mean'] for r in selected if 'oracle_nearest_reference_ca_lddt_mean' in r]
        result['summaries'][setting]=dict(targets=len(selected),eligible_multistate_targets=len(multi),coarse_valid_fraction=float(np.mean([r['coarse_valid_fraction'] for r in selected])),contact_state_coverage_at_32=float(np.mean([r['coverage']['2.0']['32'] for r in multi])) if multi else None,oracle_nearest_reference_ca_lddt_mean=float(np.mean(qualities)) if qualities else None,md_projection_wasserstein_at_32=float(np.mean([r['projection_wasserstein']['32'] for r in mdrows])) if mdrows else None)
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Ensemble state and distribution diagnostics','',f"Run: {a.run.name}.",'',result['scope']+'.','', 'Contact features are selected only from experimental references. Coverage requires a close reference contact state, CA lDDT at least 0.8, and the predeclared coarse geometry filter. All samples remain in denominators. The geometry filter does not certify physical validity. Nearest-reference quality is an oracle diagnostic.','', '| Setting | Targets | State-eligible targets | Coarse valid | State coverage @32 | Oracle CA lDDT | MD projected W1 @32 |','|---|---:|---:|---:|---:|---:|---:|']
    for setting,r in result['summaries'].items():lines.append('| '+setting+' | '+' | '.join('NA' if x is None else f'{x:.4f}' if isinstance(x,float) else str(x) for x in r.values())+' |')
    lines+=['','MD distances are in the published projection space, not Angstroms. NMR model counts are never treated as populations. Confirmation and original locked test targets remain unscored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
