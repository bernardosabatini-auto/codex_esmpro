"""Four disjoint family partitions; one fixed native budget shared across models."""
import argparse,json,math
from pathlib import Path
import h5py,numpy as np
from fragment_validation_core import raw_rows
from prepare_overfit import sha
from extra_fragment_design_panel import audit_refold_plan, designability_ids, audit_native_reuse


def partitions(lengths):
    if len(lengths)!=64 or sum(n<=256 for n in lengths.values())!=32:
        raise ValueError('Expected32short and32long families')
    short=sorted(i for i,n in lengths.items() if n<=256)
    long=sorted(i for i,n in lengths.items() if n>256)
    return [sorted(short[k::4]+long[k::4]) for k in range(4)]


def screen(c):
    for key in ('generation_manifest','protocol','fragments'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed refold screening source')
    index=json.loads(Path(c['generation_manifest']).read_text());spec=json.loads(Path(c['protocol']).read_text())
    audit_refold_plan(spec)
    if index['status']!='complete' or set(index['generations'])!=set(spec['parents']):raise ValueError('Incomplete model comparison')
    rows=[];selected={};items={}
    with h5py.File(c['fragments']) as fr:
        for ident in sorted(fr['development']):
            g=fr['development/'+ident];q=g['conditions/'+spec.get('condition','f30_center')]
            items[ident]=dict(fragment=q['fragment'][:],sequence=str(q.attrs['sequence']),start=int(q.attrs['start']),family=str(g.attrs['family']),length=int(g.attrs['length']))
        parts=partitions({i:q['length'] for i,q in items.items()})
        panel=designability_ids(spec,items)
        if c['partition'] not in range(4) or c['target_ids']!=parts[c['partition']]:raise ValueError('Changed family partition')
        for arm,r in index['generations'].items():
            for key in ('manifest','report','predictions'):
                if sha(r[key])!=r[key+'_sha256']:raise ValueError('Changed frozen generation evidence')
            m=json.loads(Path(r['manifest']).read_text());d=json.loads(Path(r['report']).read_text());gc=m['config']
            if m['status']!='complete' or d['status']!='complete' or d['controls']!=132 or d['manifest_sha256']!=r['manifest_sha256'] or d['predictions_sha256']!=r['predictions_sha256'] or m['predictions_sha256']!=r['predictions_sha256'] or gc['arm']!=arm or gc['spec']!=spec or gc['fragments']!=c['fragments'] or gc['target_ids']!=sorted(items):raise ValueError('Unqualified new-family generation')
            if Path(gc['model_manifest']).parent.name!=spec['parents'][arm]:raise ValueError('Changed model identity')
            with h5py.File(r['predictions']) as pred:
                if set(pred['new'])!=set(items):raise ValueError('Changed model inventory')
                armrows=[]
                for ident,q in items.items():
                    bb=pred['new/'+ident+'/backbone'][:]
                    if bb.shape!=(4,q['length'],4,3) or not np.isfinite(bb).all():raise ValueError('Incomplete generated sample')
                    rr=raw_rows(bb,q['fragment'],q['start'],arm,ident,q['family']);armrows.extend(rr)
                    if ident in c['target_ids']:
                        rows.extend(rr)
                        for row in rr:
                            if row['raw_gate_passed'] or ident in panel and row['generation_slot']==0:selected[arm,ident,row['generation_slot']]=bb[row['generation_slot']]
                if armrows!=d['records']:raise ValueError('Changed complete raw screening denominator')
    return rows,selected,items,spec


def audit_inputs(c,check_teacher=False):
    from teacher_numerical_recovery import audit_recovery
    audit_recovery(c)
    for key in ('predictions','usalign'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed assay input')
    if check_teacher:
        for r in c['dependencies']+c['teacher_artifacts']:
            if sha(r['path'])!=r['sha256']:raise ValueError('Changed teacher dependency')
    rows,selected,items,spec=screen(c)
    if type(c.get('teacher_deterministic_algorithms',False)) is not bool or c.get('teacher_deterministic_algorithms',False)!=spec.get('teacher_deterministic_algorithms',False):raise ValueError('Unbound teacher execution policy')
    native=audit_native_reuse(c,items,spec)
    wanted=set(selected)|({('native',i,0) for i in c['target_ids']} if native is None else set())
    if c['num_sequences']!=8 or c['temperature']!=.1 or c['mpnn_seed']!=1 or c['precision']!='fp32':raise ValueError('Changed fixed teacher budget')
    if c['screen_rows']!=rows or len(rows)!=16*4*len(spec['parents']) or c['expected_backbones']!=len(wanted) or len(c['entries'])!=len(wanted) or {(r['arm'],r['target_id'],r['generation_slot']) for r in c['entries']}!=wanted:raise ValueError('Changed unique backbone inventory')
    with h5py.File(c['predictions']) as out,h5py.File(c['fragments']) as fr:
        if set(out)!={'motifs'}|{r['dataset'] for r in c['entries']} or set(out['motifs'])!=set(c['target_ids']):raise ValueError('Changed refold input groups')
        for r in c['entries']:
            ident=r['target_id'];q=items[ident];bb=fr['references/'+ident+'/backbone'][:] if r['arm']=='native' else selected[r['arm'],ident,r['generation_slot']]
            repeat=(r['arm']=='native') if native is None else (r['arm'],ident,r['generation_slot'])==min(selected)
            if r['slot']!=0 or r['head']!=r['arm'] or r['length']!=q['length'] or r['family']!=q['family'] or r['fixed_sequence']!=q['sequence'] or r['fixed_start']!=q['start'] or r['motif_start']!=q['start'] or r['repeatability_control']!=repeat:raise ValueError('Changed supplied constraint')
            if not np.array_equal(out[r['dataset']][:],bb[None]) or not np.array_equal(out['motifs/'+ident][:],q['fragment']):raise ValueError('Changed frozen coordinates')


def main():
    p=argparse.ArgumentParser();p.add_argument('--generations',type=Path,nargs='+',required=True);p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];index=dict(status='complete',generations={});fragments=None
    for run in a.generations:
        run=run.resolve();m=json.loads((run/'manifest.json').read_text());gc=m['config'];arm=gc['arm']
        if arm in index['generations']:raise ValueError('Duplicated model')
        if fragments is not None and fragments!=gc['fragments']:raise ValueError('Different supplied fragments')
        fragments=gc['fragments'];row={}
        for key,path in [('manifest',run/'manifest.json'),('report',root/'reports'/(run.name+'.json')),('predictions',run/'predictions.h5')]:row[key]=str(path);row[key+'_sha256']=sha(path)
        index['generations'][arm]=row
    indexpath=Path(str(a.output_prefix)+'_inventory.json').resolve()
    with indexpath.open('x') as f:f.write(json.dumps(index,indent=2)+'\n')
    prior=json.loads((root/'runs/fragment_strict_followup_50112017/manifest.json').read_text())['config']
    with h5py.File(fragments) as f:parts=partitions({i:int(g.attrs['length']) for i,g in f['development'].items()})
    for k,ids in enumerate(parts):
        output=Path(str(a.output_prefix)+f'_{k}.json').resolve();c={key:prior[key] for key in ('num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign','usalign_sha256')};c.update(assay='extra_fragment_refold',partition=k,target_ids=ids,entries=[])
        for key,path in [('generation_manifest',indexpath),('protocol',Path(gc['protocol'])),('fragments',Path(fragments))]:c[key]=str(path);c[key+'_sha256']=sha(path)
        c['screen_rows'],selected,items,spec=screen(c);inputs=output.with_suffix('.h5')
        if spec.get('teacher_deterministic_algorithms'):c['teacher_deterministic_algorithms']=True
        if spec.get('native_runs'):
            native_run=root/'runs'/spec['native_runs'][k];nm=json.loads((native_run/'manifest.json').read_text());reuse={}
            for key,path in [('manifest',native_run/'manifest.json'),('report',root/'reports'/(native_run.name+'.json')),('refolded',native_run/'refolded.h5'),('predictions',Path(nm['config']['predictions']))]:reuse[key]=str(path);reuse[key+'_sha256']=sha(path)
            c['native_reuse']=reuse
        native=audit_native_reuse(c,items,spec);native_keys=[('native',i,0) for i in ids] if native is None else []
        with h5py.File(inputs,'x') as out,h5py.File(fragments) as fr:
            for ident in ids:out.create_dataset('motifs/'+ident,data=items[ident]['fragment'])
            for n,(arm,ident,slot) in enumerate(native_keys+sorted(selected)):
                repeat=(arm=='native') if native is None else (arm,ident,slot)==min(selected)
                q=items[ident];bb=fr['references/'+ident+'/backbone'][:] if arm=='native' else selected[arm,ident,slot];name=f'extra_{k}_{n:03d}';out.create_dataset(name,data=bb[None]);c['entries'].append(dict(name=name,head=arm,arm=arm,target_id=ident,family=q['family'],generation_slot=slot,slot=0,length=q['length'],dataset=name,motif_start=q['start'],fixed_start=q['start'],fixed_sequence=q['sequence'],repeatability_control=repeat))
        c['expected_backbones']=len(c['entries']);minutes=max(15,math.ceil((len(c['entries'])*8*6+180)*1.2/60));c.update(allocation_minutes=minutes,work_cap_seconds=minutes*60-90,predictions=str(inputs),predictions_sha256=sha(inputs));audit_inputs(c)
        with output.open('x') as f:f.write(json.dumps(c,indent=2)+'\n')
        print(k,len(selected),'generated',len(native_keys),'native',8*len(c['entries']),'refolds',minutes,'minutes',flush=True)

if __name__=='__main__':main()
