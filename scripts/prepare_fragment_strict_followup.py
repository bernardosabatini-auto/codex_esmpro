"""Refold every strict raw match, retaining the complete screened denominator."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.fragment_designability import motif_fit
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha


def screen(c):
    rows=[];selected={}
    for s in c['screens']:
        for key in ('manifest','report','predictions','fragments'):
            if sha(s[key])!=s[key+'_sha256']:raise ValueError('Changed screening source')
        m=json.loads(Path(s['manifest']).read_text());d=json.loads(Path(s['report']).read_text())
        if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=s['manifest_sha256']:raise ValueError('Unaudited screening source')
        with h5py.File(s['predictions']) as pred,h5py.File(s['fragments']) as fr:
            if len(fr['development'])!=16 or set(pred[s['prefix']])!=set(fr['development']):raise ValueError('Changed full development panel')
            for ident,g in fr['development'].items():
                q=g['conditions/f30_center'];bb=pred[s['prefix']+'/'+ident+'/backbone'][:];valid=backbone_geometry(bb)['coarse_valid']
                if len(bb)!=4:raise ValueError('Changed sample count')
                for slot,x in enumerate(bb):
                    fit=motif_fit(x,q['fragment'][:],int(q.attrs['start']));passed=bool(valid[slot] and fit['motif_drms']<=1 and fit['motif_ca_rmsd']<=1)
                    row=dict(arm=s['arm'],target_id=ident,family=str(g.attrs['family']),generation_slot=slot,length=len(x),raw_gate_passed=passed,coarse_valid=bool(valid[slot]),**fit);rows.append(row)
                    if passed:selected[s['arm'],ident,slot]=(x,q['fragment'][:],str(q.attrs['sequence']),int(q.attrs['start']),str(g.attrs['family']))
    return rows,selected


def audit_inputs(c,check_teacher=True):
    for key in ('generation_manifest','predictions','protocol','usalign','native_predictions'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed strict-followup source')
    if check_teacher:
        for r in c['dependencies']+c['teacher_artifacts']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed teacher artifact')
    protocol=json.loads(Path(c['protocol']).read_text())
    if [(s['arm'],Path(s['manifest']).parent.name,s['prefix']) for s in c['screens']]!=[tuple(s) for s in protocol['sources']]:raise ValueError('Unregistered screening panel')
    rows,selected=screen(c)
    if rows!=c['screen_rows'] or len(rows)!=64*len(c['screens']):raise ValueError('Screening denominator changed')
    if c.get('covered_assays'):
        from fragment_fixed_coverage import split_coverage
        selected,_=split_coverage(c,selected)
    ids=sorted({key[1] for key in selected});wanted={(arm,i,k) for arm,i,k in selected}|{('native',i,0) for i in ids}
    if c.get('expected_backbones',4)!=protocol.get('expected_backbones',4) or len(wanted)!=c.get('expected_backbones',4):raise ValueError('Unbudgeted strict followup inventory')
    if len(c['entries'])!=len(wanted) or {(r['arm'],r['target_id'],r['generation_slot']) for r in c['entries']}!=wanted:raise ValueError('Selected/dropped raw match')
    with h5py.File(c['predictions']) as out,h5py.File(c['native_predictions']) as native:
        for r in c['entries']:
            i=r['target_id'];item=next(v for k,v in selected.items() if k[1]==i) if r['arm']=='native' else selected[r['arm'],i,r['generation_slot']]
            bb=native['references/'+i+'/backbone'][:] if r['arm']=='native' else item[0]
            if r['slot']!=0 or r['length']!=len(bb) or r['family']!=item[4] or r['fixed_sequence']!=item[2] or r['fixed_start']!=item[3] or r['motif_start']!=item[3] or r['repeatability_control']!=(r['arm']=='native'):raise ValueError('Changed motif condition')
            if not np.array_equal(out[r['dataset']][0],bb) or not np.array_equal(out['motifs/'+i][:],item[1]):raise ValueError('Changed selected/native arrays')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--protocol',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=(a.protocol or root/'configs/fragment_strict_followup_protocol.json').resolve();spec=json.loads(protocol.read_text());prior=json.loads((root/'runs/trained_fragment_designability_49983356/manifest.json').read_text())['config'];c={k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};c.update(assay='fragment_strict_followup',screens=[],work_cap_seconds=480,expected_backbones=spec.get('expected_backbones',4))
    for arm,runname,prefix in spec['sources']:
        run=root/'runs'/runname;manifest=run/'manifest.json';m=json.loads(manifest.read_text());s=dict(arm=arm,prefix=prefix);step=m.get('updates');pred=run/(f'evaluation_{500 if arm in ("plain32","frame32") else step}.h5' if runname.startswith('fragment_training') else 'predictions.h5')
        for key,path in [('manifest',manifest),('report',root/'reports'/(runname+'.json')),('predictions',pred),('fragments',Path(m['config']['fragments']))]:s[key]=str(path);s[key+'_sha256']=sha(path)
        c['screens'].append(s)
    for key,path in [('generation_manifest',Path(c['screens'][min(1,len(c['screens'])-1)]['manifest'])),('protocol',protocol)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    if spec.get('covered_assays'):
        from fragment_fixed_coverage import bind_coverage
        c['covered_assays']=bind_coverage(root,spec)
    c['screen_rows'],selected=screen(c)
    if c.get('covered_assays'):
        from fragment_fixed_coverage import split_coverage
        selected,_=split_coverage(c,selected)
    ids=sorted({key[1] for key in selected});inputs=a.output.with_suffix('.h5');entries=[];frame=json.loads(Path(c['screens'][min(1,len(c['screens'])-1)]['manifest']).read_text());nativepath=Path(frame['config']['initial_predictions'])
    with h5py.File(inputs,'x') as out,h5py.File(nativepath) as native:
        for i in ids:
            item=next(v for k,v in selected.items() if k[1]==i);out.create_dataset('motifs/'+i,data=item[1])
        inventory=[('native',i,0) for i in ids]+sorted(selected)
        for index,(arm,i,k) in enumerate(inventory):
            item=next(v for key,v in selected.items() if key[1]==i) if arm=='native' else selected[arm,i,k];bb=native['references/'+i+'/backbone'][:] if arm=='native' else item[0];name=f'strict_followup_{index:03d}';out.create_dataset(name,data=bb[None]);entries.append(dict(name=name,head=arm,arm=arm,mode='native' if arm=='native' else 'generated',target_id=i,family=item[4],generation_slot=k,slot=0,length=len(bb),dataset=name,motif_start=item[3],fixed_start=item[3],fixed_sequence=item[2],repeatability_control=arm=='native'))
    c['entries']=entries
    for key,path in [('generation_manifest',Path(c['screens'][min(1,len(c['screens'])-1)]['manifest'])),('predictions',inputs),('protocol',protocol),('native_predictions',nativepath)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    audit_inputs(c,check_teacher=False);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Screened',len(c['screen_rows']),'outputs; new generated backbones',len(selected),';',len(entries)*8,'refolds withnativecontrols')


if __name__=='__main__':main()
