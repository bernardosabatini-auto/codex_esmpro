"""Export all qualified free-pose candidates, with original motif and matched budgets."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from prepare_overfit import sha


BOUND_KEYS=('generation_manifest','generation_report','generation_audit','generated_predictions','predictions',
            'protocol','baseline_refold_manifest','baseline_refold_report','parent_manifest','parent_predictions',
            'source_training_manifest','fragments','usalign')


def require_quality(d,audit):
    if (d.get('status')!='complete' or d.get('profile_only') is not False or not d.get('qualified')
            or audit.get('status')!='complete' or not audit.get('qualified')
            or audit.get('records')!=512 or audit.get('replay_max_abs')!=0
            or audit.get('matched_profile_outputs')!=64 or not audit.get('provenance_passed')
            or not audit.get('rescore_passed')):
        raise ValueError('Complete independently replayed paired full panel required')
    from evaluate_movable_motif_full import summarize
    summary,pairs,qualified=summarize(d['records'])
    expected={(p,a,r['id'],s) for p in ('fixed_pose','free_pose') for a in ('generated_cond','native_cond')
              for r in d['selected'] for s in range(4)}
    keys={(r['pose_arm'],r['arm'],r['target_id'],r['generation_slot']) for r in d['records']}
    if (len(d['selected'])!=32 or len(d['records'])!=512 or len(expected)!=512 or keys!=expected
            or summary!=d['summary'] or pairs!=d['paired'] or not qualified):
        raise ValueError('Incomplete or unqualified paired full assay')
    for r in d['records']:
        physical=bool(r['raw_gate_passed'] and r['local_geometry']['valid'] and
            r['hidden_flank_bonds']['all_edges_valid'] and r['junctions']['valid'])
        eligible=bool(physical and r['nonbonded']['pairs_below_threshold']==0)
        if (physical!=r['refold_eligible_geometry'] or eligible!=r['steric_eligible']
                or not r['far_exact'] or r['motif_rigid_rmsd']>1e-4 or r['motif_pair_distance_max_error']>1e-4):
            raise ValueError('Changed physical and rigid-fragment gate')
    return sum(r['steric_eligible'] for r in d['records'] if r['arm']=='generated_cond' and r['pose_arm']=='free_pose')


from torsion_closure_refolding import file_inventory,file_stats,config_digest,audit_worker


def audit_refold(c,*,audited_generation=None,verify_teacher=True):
    if c.get('torsion_closure_refold') is not True or c.get('movable_motif_refold') is not True:raise ValueError('Explicit movable-motif assay required')
    for key in BOUND_KEYS:
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed closure-refold input: '+key)
    if verify_teacher:
        for dep in c['dependencies']+c['teacher_artifacts']:
            if sha(dep['path'])!=dep['sha256']:raise ValueError('Changed teacher dependency')
    d=json.loads(Path(c['generation_report']).read_text());a=json.loads(Path(c['generation_audit']).read_text())
    count=require_quality(d,a);gm=json.loads(Path(c['generation_manifest']).read_text())
    spec=json.loads(Path(c['protocol']).read_text())
    bm=json.loads(Path(c['baseline_refold_manifest']).read_text());bd=json.loads(Path(c['baseline_refold_report']).read_text());bc=bm['config']
    pm=json.loads(Path(c['parent_manifest']).read_text());pg=pm['config']
    tm=json.loads(Path(c['source_training_manifest']).read_text());tc=tm['config']
    if (d['manifest_sha256']!=c['generation_manifest_sha256'] or d['predictions_sha256']!=c['generated_predictions_sha256']
            or gm['predictions_sha256']!=c['generated_predictions_sha256'] or gm['records']!=d['records']
            or a['full_report_sha256']!=c['generation_report_sha256'] or a['predictions_sha256']!=c['generated_predictions_sha256']
            or Path(c['generation_manifest']).parent.name!=spec['source_run'] or spec['samples']!=128
            or spec['required_complete_geometry']!=45 or spec['sequences_per_backbone']!=8
            or bm['status']!='complete' or bd['status']!='complete' or bd['completed_refolds']!=256
            or bd['manifest_sha256']!=c['baseline_refold_manifest_sha256'] or not bm['teacher_deterministic_algorithms']
            or bc['generation_manifest']!=c['parent_manifest'] or bc['generated_predictions']!=c['parent_predictions']
            or pg['arm']!='parent6000' or pg['selected']!=d['selected'] or pg['selected']!=tc['selected']
            or pg['fragments']!=c['fragments'] or tc['fragments']!=c['fragments']
            or any(c[k]!=bc[k] for k in TEACHER_KEYS) or c['num_sequences']!=8 or c['temperature']!=.1
            or c['assay']!='fragment_preference_refold' or c['partition'] not in range(4) or c['arm']!='movable_motif'
            or c['expected_backbones']!=32 or len(c['entries'])!=32 or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010
            or c.get('teacher_deterministic_algorithms') is not True or c.get('mpnn_mode')!='ca'):
        raise ValueError('Changed construction, historical controls or matched teacher budget')
    selected=[r for r in d['selected'] if r['partition']==c['partition']]
    wanted=[]
    with h5py.File(c['fragments'],'r',locking=False) as fr,h5py.File(c['predictions'],'r',locking=False) as out,h5py.File(c['generated_predictions'],'r',locking=False) as gen,h5py.File(c['parent_predictions'],'r',locking=False) as parent:
        for row in selected:
            q=fr['train/'+row['id']+'/conditions/c20_center']
            if not np.array_equal(out['motifs/'+row['id']][:],q['fragment'][:]):raise ValueError('Changed ORIGINAL supplied motif')
            for slot in range(4):
                entry=make_entry(row,q,slot,len(wanted),arm='movable_motif');wanted.append(entry)
                key='free_pose/generated_cond/'+row['id']+'/'+str(slot)
                if (not np.array_equal(out[entry['dataset']][:],gen[key+'/backbone'][:][None])
                        or not np.array_equal(gen[key+'/parent'][:],parent['new/'+row['id']+'/backbone'][slot].astype(np.float64))):
                    raise ValueError('Changed constructed backbone or original unconditional parent')
        if c['entries']!=wanted or set(out)!={'motifs'}|{r['dataset'] for r in wanted} or set(out['motifs'])!={r['id'] for r in selected}:
            raise ValueError('Filtered or changed128-candidate assay')
    gc=dict(arm='movable_motif',selected=d['selected'],fragments=c['fragments'],native_sources=pg['native_sources'],
            torsion_closure_refold=True,movable_motif_refold=True,eligible_geometry=count)
    if audited_generation is not None and audited_generation!=(gc,spec):raise ValueError('Changed previously audited closure generation')
    return gc,spec


def prepare(root,protocol,prefix):
    spec=json.loads(protocol.read_text());report=root/spec['source_report'];audit_path=root/spec['source_audit']
    d=json.loads(report.read_text());a=json.loads(audit_path.read_text());require_quality(d,a)
    # Independently repeat replay/scoring once before exporting any GPU inputs.
    from evaluate_movable_motif_full import audit_full
    if audit_full(root,report)!=a:raise ValueError('Stored final closure audit changed')
    run=Path(d['run']);baseline=json.loads(Path(d['baseline_report']).read_text());old_report=json.loads((root/baseline['spec']['source_report']).read_text())
    source_manifest=Path(old_report['manifest_path']);tc=json.loads(source_manifest.read_text())['config']
    checksum_cache={}
    comparison=json.loads((root/'reports/fragment_preference_comparison_20261003.json').read_text())
    parents={}
    for row in comparison['sources']:
        path=Path(row['report'])
        if sha(path)!=row['report_sha256']:raise ValueError('Changed original parent partition')
        report_data=json.loads(path.read_text());bm=root/'runs'/path.stem/'manifest.json'
        if sha(bm)!=report_data['manifest_sha256']:raise ValueError('Changed parent manifest')
        config=json.loads(bm.read_text())['config'];partition=config['partition']
        if partition in parents:raise ValueError('Duplicate parent partition')
        parents[partition]=(path,bm,config)
    if set(parents)!=set(range(4)):raise ValueError('Four distinct original parent partitions required')
    for partition in range(4):
        baseline_report,bm,bc=parents[partition]
        prior=bc
        path=Path(str(prefix)+f'_{partition}.json').resolve();inputs=path.with_suffix('.h5')
        c={k:prior[k] for k in TEACHER_KEYS}
        c.update(assay='fragment_preference_refold',torsion_closure_refold=True,movable_motif_refold=True,arm='movable_motif',partition=partition,
            expected_backbones=32,entries=[],allocation_minutes=35,work_cap_seconds=2010,teacher_deterministic_algorithms=True,mpnn_mode='ca')
        sources=dict(generation_manifest=run/'manifest.json',generation_report=report,generation_audit=audit_path,
            generated_predictions=run/'predictions.h5',protocol=protocol,baseline_refold_manifest=bm,
            baseline_refold_report=baseline_report,parent_manifest=Path(bc['generation_manifest']),
            parent_predictions=Path(bc['generated_predictions']),source_training_manifest=source_manifest,fragments=Path(tc['fragments']))
        for key,value in sources.items():c[key]=str(value.resolve());c[key+'_sha256']=sha(value)
        with h5py.File(c['fragments'],'r',locking=False) as fr,h5py.File(c['generated_predictions'],'r',locking=False) as gen,h5py.File(inputs,'x',locking=False) as out:
            for row in (r for r in d['selected'] if r['partition']==partition):
                q=fr['train/'+row['id']+'/conditions/c20_center'];out['motifs/'+row['id']]=q['fragment'][:]
                for slot in range(4):
                    entry=make_entry(row,q,slot,len(c['entries']),arm='movable_motif');c['entries'].append(entry)
                    out[entry['dataset']]=gen['free_pose/generated_cond/'+row['id']+'/'+str(slot)+'/backbone'][:][None]
        c.update(predictions=str(inputs),predictions_sha256=sha(inputs))
        gc,sp=audit_refold(c,verify_teacher=False)
        before=file_stats(c)
        for row in before:
            key=tuple(sorted(row.items()))
            if key not in checksum_cache:
                if sha(row['path'])!=row['sha256']:raise ValueError('CPU input/teacher content verification failed')
                checksum_cache[key]=True
        if file_stats(c)!=before:raise ValueError('Files changed during CPU content verification')
        c['cpu_verified_file_stats']=before;c['cpu_verified_config_sha256']=config_digest(c);audit_worker(c)
        with path.open('x') as f:json.dump(c,f,indent=2);f.write('\n')
        print('prepared',partition,len(c['entries']),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path,default=Path('configs/movable_motif_refold_protocol.json'))
    p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args()
    prepare(Path(__file__).resolve().parents[1],a.protocol,a.output_prefix)


if __name__=='__main__':main()
