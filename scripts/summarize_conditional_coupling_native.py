"""Audit all native-screen predictions for a qualified conditional coupling pair."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.teacher_states import paired_change
from prepare_overfit import sha


def analyze(run,m):
    c=m['config']
    for key in ('selection','protocol','capacity_report','baseline_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());capacity=json.loads(Path(c['capacity_report']).read_text());selection=json.loads(Path(c['selection']).read_text());families={r['id']:r['family'] for r in selection['tuning']}
    settings=[('original',1),('original',2),('independent',1),('optimal',1)]
    if protocol['heads']!=['original','independent','optimal'] or protocol['guidance_by_head']!={'original':[1,2],'independent':[1],'optimal':[1]} or [h['name'] for h in c['heads']]!=protocol['heads']:raise ValueError('Unexpected screen arms')
    if len(families)!=64 or len(set(families.values()))!=64 or c['training_family_count']!=32 or c['training_checkpoint_step']!=500 or m['training_updates_executed']!=0 or not capacity['qualified_for_replication_and_native']:raise ValueError('Invalid transfer scope')
    for head in c['heads']:
        if sha(head['checkpoint'])!=head['checkpoint_sha256']:raise ValueError('Changed checkpoint')
        if head.get('training_manifest') and sha(head['training_manifest'])!=head['training_manifest_sha256']:raise ValueError('Changed training evidence')
    controls=m['controls'];expected={(h,g,b) for h,g in settings for b in (128,256,384,512)}
    if len(controls)!=16 or {(r['head'],r['guidance'],r['length']) for r in controls}!=expected or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('Failed or missing batching controls')
    scores=m['scores'];expected={(h,g,i,k) for h,g in settings for i in families for k in range(3)};indexed={(r['head'],r['guidance'],r['target_id'],r['sample']):r for r in scores}
    if len(scores)!=768 or set(indexed)!=expected or any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in scores for k in ('ca_lddt','coarse_valid')):raise ValueError('Invalid score coverage')
    prior=json.loads(Path(c['baseline_manifest']).read_text());baseline={(r['target_id'],r['sample']):r for r in prior['scores'] if r['step']==0 and r['sampling_steps']==25}
    checked=0
    with h5py.File(run/'predictions.h5') as predictions,h5py.File(selection['dataset']) as source:
        if set(predictions)!=set(protocol['heads']):raise ValueError('Archived head coverage')
        for h,g in settings:
            group=predictions[f'{h}/cfg{g}']
            if set(group)!=set(families):raise ValueError('Archived family coverage')
            for ident in families:
                bb=group[ident][:];reference=source['train'][ident]['ca_coords'][:]
                if len(bb)!=3 or bb.shape[1]!=len(reference):raise ValueError('Archived sample shape')
                geometry=backbone_geometry(bb)
                for k,x in enumerate(bb):
                    actual={**ca_metrics(x[:,1],reference),**{key:float(value[k]) for key,value in geometry.items()}};saved=indexed[h,g,ident,k]
                    if any(not np.isfinite(v) or abs(v-saved[key])>1e-6 for key,v in actual.items()):raise ValueError('Archived structural score mismatch')
                    if (h,g)==('original',2) and any(abs(saved[key]-baseline[ident,k][key])>1e-6 for key in ('ca_lddt','coarse_valid')):raise ValueError('Original baseline changed')
                    checked+=1
    values={(h,g):{key:{i:float(np.mean([indexed[h,g,i,k][key] for k in range(3)])) for i in families} for key in ('ca_lddt','coarse_valid')} for h,g in settings}
    def compare(a,b):return {key:paired_change(values[a][key],values[b][key],families=families) for key in ('ca_lddt','coarse_valid')}
    def qualified(metrics):return metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01
    summaries={f'{h}_cfg{g}':compare((h,g),('original',2)) for h,g in settings};effect=compare(('optimal',1),('independent',1))
    return dict(summaries=summaries,pairing_effect=effect,optimal_vs_original_cfg1=compare(('optimal',1),('original',1)),quality_passed=bool(qualified(summaries['optimal_cfg1']) and qualified(effect)),archived_predictions_audited=checked,elapsed_seconds=m['elapsed_seconds'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':d.update(analyze(a.runs[0],m));d['manifest_sha256']=sha(path)
    else:d['error']=m.get('error','Incomplete screen')
    lines=['# Conditional coupling: separate accuracy screen','',f"Status: {d['status']}.",'','64 tuning families with predicted references; three fixed samples. No locked tests, training replication or model promotion. All failed geometries retained.','','| Head | CA-lDDT | Delta vs original CFG2 |95% family interval | Valid | Validity delta |','|---|---:|---:|---|---:|---:|']
    for name,r in d.get('summaries',{}).items():
        ca=r['ca_lddt'];v=r['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} |")
    if d['status']=='complete':
        r=d['pairing_effect'];lines+=['',f"Optimal minus independent: CA-lDDT {r['ca_lddt']['difference']:+.5f},95% family interval {r['ca_lddt']['ci95']}; validity {r['coarse_valid']['difference']:+.5f}.",'',f"Quality qualified: {d['quality_passed']}. All{d['archived_predictions_audited']}archived predictions audited. Separate replication and external diversity evidence remain required."]
    else:lines+=['',d['error']]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
