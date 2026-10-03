"""Refold each unique fresh raw match once, preserving both analysis views."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from fragment_validation_core import audit_config,raw_rows
from prepare_overfit import sha


def screen(c):
    for key in ('generation_manifest','generation_report','generation_predictions','fragments','protocol'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed validation screening source')
    m=json.loads(Path(c['generation_manifest']).read_text());d=json.loads(Path(c['generation_report']).read_text());gc=m['config'];audit_config(gc)
    if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=c['generation_manifest_sha256'] or m['predictions_sha256']!=c['generation_predictions_sha256'] or gc['fragments']!=c['fragments'] or gc['protocol']!=c['protocol']:raise ValueError('Unaudited fresh generation')
    rows=[];selected={};items={}
    with h5py.File(c['generation_predictions']) as pred,h5py.File(c['fragments']) as fr:
        for arm in gc['models']:
            for ident in gc['target_ids']:
                v=fr['development/'+ident];q=v['conditions/'+gc['spec']['condition']];item=(q['fragment'][:],str(q.attrs['sequence']),int(q.attrs['start']),str(v.attrs['family']));items[ident]=item;bb=pred[arm+'/'+ident+'/backbone'][:]
                if bb.shape!=((16 if ident==gc['spec']['focus_id'] else 4),int(v.attrs['length']),4,3):raise ValueError('Changed fresh inventory')
                rr=raw_rows(bb,item[0],item[2],arm,ident,item[3]);rows.extend(rr)
                for r in rr:
                    if r['raw_gate_passed']:selected[arm,ident,r['generation_slot']]=(bb[r['generation_slot']],*item)
    if len(rows)!=152 or rows!=d['records']:raise ValueError('Changed complete screening denominator')
    return rows,selected,items,gc


def audit_inputs(c,check_teacher=False):
    for key in ('predictions','native_predictions','usalign'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed validation refold input')
    if check_teacher:
        for r in c['dependencies']+c['teacher_artifacts']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed teacher dependency')
    rows,selected,items,gc=screen(c);ids={key[1] for key in selected}|{gc['spec']['focus_id']};wanted=set(selected)|{('native',i,0) for i in ids}
    if rows!=c['screen_rows'] or c['native_predictions']!=gc['native_predictions'] or len(c['entries'])!=len(wanted) or c['expected_backbones']!=len(wanted) or {(r['arm'],r['target_id'],r['generation_slot']) for r in c['entries']}!=wanted:raise ValueError('Duplicated, dropped or added backbone')
    with h5py.File(c['predictions']) as out,h5py.File(c['native_predictions']) as native:
        if set(out)!={'motifs'}|{r['dataset'] for r in c['entries']} or set(out['motifs'])!=ids:raise ValueError('Unexpected input groups')
        for r in c['entries']:
            ident=r['target_id'];item=items[ident];bb=native['references/'+ident+'/backbone'][:] if r['arm']=='native' else selected[r['arm'],ident,r['generation_slot']][0]
            if r['slot']!=0 or r['length']!=len(bb) or r['family']!=item[3] or r['fixed_sequence']!=item[1] or r['fixed_start']!=item[2] or r['motif_start']!=item[2] or r['repeatability_control']!=(r['arm']=='native'):raise ValueError('Changed supplied motif')
            if not np.array_equal(out[r['dataset']][:],bb[None]) or not np.array_equal(out['motifs/'+ident][:],item[0]):raise ValueError('Changed backbone or fragment arrays')


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=a.generation.resolve();m=json.loads((run/'manifest.json').read_text());gc=m['config']
    prior=json.loads((root/'runs/fragment_strict_followup_50051910/manifest.json').read_text())['config'];c={k:prior[k] for k in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};c.update(assay='fragment_validation_refold',entries=[])
    for key,path in [('generation_manifest',run/'manifest.json'),('generation_report',root/'reports'/(run.name+'.json')),('generation_predictions',run/'predictions.h5'),('fragments',Path(gc['fragments'])),('protocol',Path(gc['protocol']))]:c[key]=str(path);c[key+'_sha256']=sha(path)
    c['screen_rows'],selected,items,gc=screen(c);ids=sorted({key[1] for key in selected}|{gc['spec']['focus_id']});nativepath=Path(gc['native_predictions']);inputs=a.output.with_suffix('.h5').resolve()
    with h5py.File(inputs,'x') as out,h5py.File(nativepath) as native:
        for ident in ids:out.create_dataset('motifs/'+ident,data=items[ident][0])
        for index,(arm,ident,slot) in enumerate([('native',i,0) for i in ids]+sorted(selected)):
            item=items[ident];bb=native['references/'+ident+'/backbone'][:] if arm=='native' else selected[arm,ident,slot][0];name=f'validation_{index:03d}';out.create_dataset(name,data=bb[None]);c['entries'].append(dict(name=name,head=arm,arm=arm,target_id=ident,family=item[3],generation_slot=slot,slot=0,length=len(bb),dataset=name,motif_start=item[2],fixed_start=item[2],fixed_sequence=item[1],repeatability_control=arm=='native'))
    c['expected_backbones']=len(c['entries']);minutes=max(10,math.ceil((len(c['entries'])*8*6+180)*1.2/60));c.update(allocation_minutes=minutes,work_cap_seconds=minutes*60-90)
    for key,path in [('predictions',inputs),('native_predictions',nativepath)]:c[key]=str(path);c[key+'_sha256']=sha(path)
    audit_inputs(c);a.output.write_text(json.dumps(c,indent=2)+'\n');print('Unique raw matches',len(selected),'native controls',len(ids),'refolds',8*len(c['entries']),'allocation minutes',minutes)

if __name__=='__main__':main()
