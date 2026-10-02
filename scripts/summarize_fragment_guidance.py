"""Audit a fixed guidance contrast, including motif-aligned scaffold diversity."""
import argparse,json,itertools
from pathlib import Path
import h5py,numpy as np
from latentfold.fragment_designability import motif_fit
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from train_fragment_conditioning import load_data
from summarize_fragment_training import interval
from prepare_overfit import sha


from latentfold.fragment_designability import scaffold_rmsd


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'))
    c=m['config']
    for key in ('generation_manifest','training_report','checkpoint','fragments','parent_predictions','decoder_checkpoint','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if m['training_updates'] or c['guidance']!=[1,2] or c['samples']!=4 or c['steps']!=50 or sha(run/'predictions.h5')!=m['predictions_sha256']:raise ValueError('Recipe/output mismatch')
    data=load_data(c['fragments']);ids=sorted(i for cohort,i in data if cohort=='development')
    expected={(g,i,k) for g in (1,2) for i in ids for k in range(4)};records=m['records']
    if len(ids)!=16 or len(records)!=128 or {(r['guidance'],r['target_id'],r['slot']) for r in records}!=expected:raise ValueError('Incomplete output coverage')
    expected_controls={('historical_conditioned',i) for i in ids}|{(kind,i) for kind in ('historical_null','guided_pose') for i in c['control_ids']}
    if len(m['controls'])!=len(expected_controls) or {(r['kind'],r['target_id']) for r in m['controls']}!=expected_controls:raise ValueError('Incomplete controls')
    for r in m['controls']:
        if r['latent_max_abs']>(1e-4 if r['kind']=='guided_pose' else 1e-5):raise ValueError('Latent control failed')
        if r['kind']=='historical_conditioned' and (r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99 or not r['same_validity']):raise ValueError('Geometry control failed')
    indexed={(r['guidance'],r['target_id'],r['slot']):r for r in records};diversity=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['parent_predictions']) as old:
        if set(f)!={'guidance1','guidance2'}:raise ValueError('Unexpected mode')
        for guidance in (1,2):
            if set(f[f'guidance{guidance}'])!=set(ids):raise ValueError('Target inventory mismatch')
            for ident in ids:
                v=data['development',ident];q=v['conditions']['f30_center'];keep=q['keep'].numpy();start=int(np.where(keep)[0][0]);g=f[f'guidance{guidance}/{ident}'];bb=g['backbone'][:];z=g['latent'][:]
                if len(bb)!=4 or len(z)!=4 or not np.isfinite(bb).all() or not np.isfinite(z).all():raise ValueError('Invalid saved arrays')
                valid=backbone_geometry(bb)['coarse_valid'];qualified=[]
                for k in range(4):
                    r=indexed[guidance,ident,k];fit=motif_fit(bb[k],q['fragment'],start)
                    if r['family']!=v['family'] or r['coarse_valid']!=bool(valid[k]) or any(abs(r[key]-val)>1e-7 for key,val in fit.items()):raise ValueError('Saved metric mismatch')
                    r['strict_raw']=bool(valid[k] and fit['motif_drms']<=1 and fit['motif_ca_rmsd']<=1);qualified.append(r['strict_raw'])
                if guidance==1:
                    baseline=old['development/conditioned/'+ident];oldbb=baseline['backbone'][:]
                    if np.max(abs(z-baseline['latent'][:]))>1e-5 or not np.array_equal(valid,backbone_geometry(oldbb)['coarse_valid']):raise ValueError('Historical arrays differ')
                    for x,y in zip(bb,oldbb):
                        score=ca_metrics(x[:,1],y[:,1])
                        if score['ca_rmsd']>.2 or score['ca_lddt']<.99:raise ValueError('Historical structure differs')
                for i,j in itertools.combinations(range(4),2):diversity.append(dict(guidance=guidance,target_id=ident,qualified=qualified[i] and qualified[j],scaffold_rmsd=scaffold_rmsd(bb[i],bb[j],keep)))
    families=sorted({r['family'] for r in records});comparisons=[];summaries=[]
    for metric in ('strict_raw','coarse_valid','motif_drms','motif_ca_rmsd'):
        means=[[np.mean([r[metric] for r in records if r['guidance']==g and r['family']==family]) for family in families] for g in (1,2)]
        comparisons.append(dict(metric=metric,guidance1=float(np.mean(means[0])),guidance2=float(np.mean(means[1])),guidance2_minus_1=interval(np.array(means[1])-means[0])))
    for g in (1,2):
        rr=[r for r in records if r['guidance']==g];dd=[r for r in diversity if r['guidance']==g];qq=[r for r in dd if r['qualified']]
        summaries.append(dict(guidance=g,samples=len(rr),valid=sum(r['coarse_valid'] for r in rr),strict_raw=sum(r['strict_raw'] for r in rr),all_diversity_pairs=len(dd),mean_scaffold_rmsd=float(np.mean([r['scaffold_rmsd'] for r in dd])),qualified_diversity_pairs=len(qq),qualified_mean_scaffold_rmsd=float(np.mean([r['scaffold_rmsd'] for r in qq])) if qq else None))
    batches=m['batches']
    if len(batches)!=32 or {(r['guidance'],r['target_id']) for r in batches}!={(g,i) for g in (1,2) for i in ids}:raise ValueError('Incomplete timing coverage')
    for r in batches:
        if r['velocity_evaluations']!=50*r['guidance'] or not np.isfinite(r['seconds']) or r['seconds']<=0:raise ValueError('Invalid timing')
    fixed=[r for r in records if r['guidance']==2 and r['target_id'] in c['control_ids'] and r['slot']<2];strict=next(r for r in comparisons if r['metric']=='strict_raw');valid=next(r for r in comparisons if r['metric']=='coarse_valid');gate=any(r['strict_raw'] for r in fixed) and strict['guidance2_minus_1']['mean']>0 and valid['guidance2_minus_1']['ci95'][0]>=-.05
    return dict(status='complete',manifest_sha256=sha(path),predictions_sha256=m['predictions_sha256'],designability_followup_qualified=bool(gate),fixed_assay_raw_success=sum(r['strict_raw'] for r in fixed),summaries=summaries,comparisons=comparisons,timing=[dict(guidance=g,seconds=sum(r['seconds'] for r in batches if r['guidance']==g),peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in batches if r['guidance']==g)) for g in (1,2)],elapsed_seconds=m['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fixed fragment guidance screen\n\nSixteen development families, four matched noises, CFG1 versus CFG2. Every output retained and audited. Scaffold diversity is measured after proper motif alignment; qualified-pair counts expose sparse success. Raw geometry and motif retention do not demonstrate designability.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
