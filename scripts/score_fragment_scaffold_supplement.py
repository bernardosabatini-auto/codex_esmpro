"""Same-refold scaffold agreement for fixed assays and reused strict followups."""
import argparse,itertools,json
from contextlib import ExitStack
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import usalign_coordinates
from latentfold.fragment_designability import motif_fit,scaffold_rmsd
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha


def analyze(run,report):
    d=json.loads(report.read_text());root=run.resolve().parent.parent
    if d['status']!='complete' or d['manifest_sha256']!=sha(run/'manifest.json') or d['refolded_sha256']!=sha(run/'refolded.h5'):raise ValueError('Changed audited primary assay')
    records=d.get('records',d.get('backbones'));rows=[];sources={};backbone_sources={};diversity=[]
    with ExitStack() as stack:
        for r in records:
            source=Path(r.get('reused_from',run)).resolve();name=r.get('source_name',r['name'])
            if str(source) not in sources:
                path=source/'manifest.json';m=json.loads(path.read_text());c=m['config'];sd=d if source==run.resolve() else json.loads((root/'reports'/(source.name+'.json')).read_text())
                if m['status']!='complete' or sd['status']!='complete' or sd['manifest_sha256']!=sha(path) or sd['refolded_sha256']!=sha(source/'refolded.h5') or c['predictions_sha256']!=sha(c['predictions']) or c['usalign_sha256']!=sha(c['usalign']):raise ValueError('Changed source assay')
                sources[str(source)]=dict(manifest=m,raw=stack.enter_context(h5py.File(c['predictions'])),folds=stack.enter_context(h5py.File(source/'refolded.h5')),manifest_sha256=sha(path),refolded_sha256=sd['refolded_sha256'])
            source_data=sources[str(source)];m=source_data['manifest'];raw=source_data['raw'];folds=source_data['folds'];entry=next(x for x in m['config']['entries'] if x['name']==name)
            if r.get('source_manifest_sha256',source_data['manifest_sha256'])!=source_data['manifest_sha256'] or entry['target_id']!=r['target_id'] or entry['motif_start']!=r['motif_start']:raise ValueError('Changed reused source mapping')
            x=raw[entry['dataset']][:] if entry['head']=='experimental' else raw[entry['dataset']][entry['slot']];fragment=raw['motifs/'+r['target_id']][:];start=r['motif_start'];keep=np.ones(len(x),bool);keep[start:start+len(fragment)]=False
            identity=(r.get('arm',r.get('mode')),r['target_id'],r.get('generation_slot',r.get('slot')))
            if identity in backbone_sources:raise ValueError('Duplicate backbone identity')
            backbone_sources[identity]=(str(source),name,start,len(fragment))
            if len(r['refolds'])!=8 or set(folds[name])!=set(map(str,range(8))):raise ValueError('Changed eight-design budget')
            for k,reference in enumerate(r['refolds']):
                y=folds[name+'/'+str(k)][:];tm=usalign_coordinates(m['config']['usalign'],y[:,1],x[:,1]);fit=motif_fit(y,fragment,start);valid=bool(backbone_geometry(y[None])['coarse_valid'][0])
                if abs(tm-reference['sc_tm'])>1e-7 or valid!=reference['coarse_valid'] or any(abs(fit[key]-reference[key])>1e-5 for key in fit):raise ValueError('Changed same-refold evidence')
                scaffold=usalign_coordinates(m['config']['usalign'],y[keep,1],x[keep,1]);primary_success=r['raw_gate_passed'] and k in r['successful_refold_indices'];rows.append(dict(arm=r.get('arm',r.get('mode')),target_id=r['target_id'],generation_slot=r.get('generation_slot',r.get('slot')),sequence_index=k,primary_joint_success=primary_success,scaffold_joint_success=primary_success and scaffold>.5,global_tm=tm,scaffold_only_tm=scaffold))
        first={}
        for row in rows:
            key=(row['arm'],row['target_id'],row['generation_slot'])
            if row['scaffold_joint_success'] and key not in first:first[key]=row['sequence_index']
        for arm,ident in sorted({key[:2] for key in first}):
            keys=sorted(key for key in first if key[:2]==(arm,ident));pairs=[]
            for left,right in itertools.combinations(keys,2):
                ls,ln,start,length=backbone_sources[left];rs,rn,_,_=backbone_sources[right];x=sources[ls]['folds'][ln+'/'+str(first[left])][:];y=sources[rs]['folds'][rn+'/'+str(first[right])][:];motif=np.zeros(len(x),bool);motif[start:start+length]=True;binary=sources[ls]['manifest']['config']['usalign']
                pairs.append(dict(left_slot=left[2],right_slot=right[2],left_sequence=first[left],right_sequence=first[right],global_tm=usalign_coordinates(binary,x[:,1],y[:,1]),scaffold_tm=usalign_coordinates(binary,x[~motif,1],y[~motif,1]),motif_aligned_scaffold_rmsd=scaffold_rmsd(x,y,motif)))
            diversity.append(dict(arm=arm,target_id=ident,successful_backbones=len(keys),pairs=pairs))
    counts={arm:len({(r['target_id'],r['generation_slot']) for r in rows if r['arm']==arm and r['scaffold_joint_success']}) for arm in sorted({r['arm'] for r in rows})}
    return dict(status='complete',source_report_sha256=sha(report),scored_refolds=len(rows),scaffold_joint_backbones=counts,source_hashes={key:{k:value[k] for k in ('manifest_sha256','refolded_sha256')} for key,value in sources.items()},rows=rows,successful_scaffold_diversity=diversity,scope='Supplement adds scaffold-onlyTM>0.5 to the SAME valid refold satisfying every original strict criterion. Exactly eight designs per backbone, including explicitly reused fixed-assay outputs. No historical sequence budgets pooled. Original screening denominators and failures remain in the primary report; counts are distinct backbones, not sequences.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.run,a.report);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Same-refold scaffold agreement\n\n'+d['scope']+'\n\n```json\n'+json.dumps({k:d[k] for k in ('scored_refolds','scaffold_joint_backbones','source_report_sha256')},indent=2)+'\n```\n');print(json.dumps(d['scaffold_joint_backbones']))


if __name__=='__main__':main()
