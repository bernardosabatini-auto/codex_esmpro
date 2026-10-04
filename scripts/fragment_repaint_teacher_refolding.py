"""Complete matched-budget refolding for the qualified oracle teacher."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from fragment_repaint_teacher_core import audit,eligibility
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from prepare_overfit import sha


def require_generation(d):
    if d.get('status')!='complete' or d.get('oracle_teacher') is not True or d.get('controls')!=8:
        raise ValueError('Audited oracle teacher required')
    rows=[r for r in d['records'] if r['arm']=='oracle_repaint'];gate=eligibility(rows)
    if gate!=d['refold_eligibility'] or not gate['qualified']:raise ValueError('Teacher cannot meet same-refold counts')


def audit_refold(c,*,audited_generation=None):
    from prepare_fragment_preference_refold import audit_inputs
    if c.get('oracle_teacher_refold') is not True:raise ValueError('Explicit oracle-refold flag required')
    for key in ('generation_manifest','generation_report','generated_predictions','predictions','protocol','baseline_refold_manifest','baseline_refold_report'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed oracle refold input:'+key)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];d=json.loads(Path(c['generation_report']).read_text())
    if audited_generation is None:audit(gc)
    require_generation(d);spec=gc['spec']
    result=dict(gc,oracle_teacher_refold=True,prediction_group='new')
    if audited_generation is not None and audited_generation!=(result,spec):raise ValueError('Changed audited teacher source')
    bm=json.loads(Path(c['baseline_refold_manifest']).read_text());bd=json.loads(Path(c['baseline_refold_report']).read_text());bc=bm['config']
    if audited_generation is None:original,_=audit_inputs(bc)
    else:original=json.loads(Path(bc['generation_manifest']).read_text())['config']
    if (gm['status']!='complete' or d['manifest_sha256']!=c['generation_manifest_sha256'] or d['predictions_sha256']!=c['generated_predictions_sha256']
            or gm['predictions_sha256']!=c['generated_predictions_sha256'] or d['protocol_sha256']!=c['protocol_sha256'] or c['protocol']!=gc['protocol']
            or bm['status']!='complete' or bd['status']!='complete' or bd['manifest_sha256']!=c['baseline_refold_manifest_sha256'] or bd['completed_refolds']!=256
            or original['selected']!=gc['selected'] or original['native_sources']!=gc['native_sources'] or original['arm']!='parent6000'
            or bc['generation_manifest']!=gc['baseline_manifest'] or bc['generated_predictions']!=gc['baseline_predictions']
            or c['assay']!='fragment_preference_refold' or c['partition'] not in range(4) or c['arm']!='oracle_repaint'
            or c['expected_backbones']!=32 or len(c['entries'])!=32 or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010
            or c.get('teacher_deterministic_algorithms') is not True or not bm['teacher_deterministic_algorithms']
            or c.get('mpnn_mode','ca')!='ca' or any(c[k]!=bc[k] for k in TEACHER_KEYS)):
        raise ValueError('Changed matched oracle teacher refolding recipe')
    rows=[r for r in gc['selected'] if r['partition']==c['partition']]
    with h5py.File(gc['fragments']) as fr,h5py.File(c['predictions']) as out,h5py.File(c['generated_predictions']) as gen:
        wanted=[]
        for row in rows:
            q=fr['train/'+row['id']+'/conditions/c20_center']
            for slot in range(4):wanted.append(make_entry(row,q,slot,len(wanted),arm='oracle_repaint'))
        if wanted!=c['entries'] or set(out)!={'motifs'}|{r['dataset'] for r in wanted} or set(out['motifs'])!={r['id'] for r in rows}:raise ValueError('Filtered teacher population')
        for r in wanted:
            if not np.array_equal(out[r['dataset']][:],gen['new/'+r['target_id']+'/backbone'][r['generation_slot']][None]) or not np.array_equal(out['motifs/'+r['target_id']][:],fr['train/'+r['target_id']+'/conditions/c20_center/fragment'][:]):raise ValueError('Changed supplied motif or teacher backbone')
    return result,spec


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--baseline-run',type=Path,required=True);p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.generation.resolve();base=a.baseline_run.resolve()
    gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];audit(gc);report=root/'reports'/(run.name+'.json');require_generation(json.loads(report.read_text()))
    bc=json.loads((base/'manifest.json').read_text())['config'];cached=None
    for partition in range(4):
        path=Path(str(a.output_prefix)+f'_{partition}.json').resolve();inputs=path.with_suffix('.h5')
        c={k:bc[k] for k in TEACHER_KEYS};c.update(oracle_teacher_refold=True,assay='fragment_preference_refold',arm='oracle_repaint',partition=partition,expected_backbones=32,entries=[],allocation_minutes=35,work_cap_seconds=2010,teacher_deterministic_algorithms=True)
        for key,value in [('generation_manifest',run/'manifest.json'),('generation_report',report),('generated_predictions',run/'predictions.h5'),('protocol',gc['protocol']),('baseline_refold_manifest',base/'manifest.json'),('baseline_refold_report',root/'reports'/(base.name+'.json'))]:c[key]=str(value);c[key+'_sha256']=sha(value)
        with h5py.File(gc['fragments']) as fr,h5py.File(run/'predictions.h5') as gen,h5py.File(inputs,'x') as out:
            for row in (r for r in gc['selected'] if r['partition']==partition):
                q=fr['train/'+row['id']+'/conditions/c20_center'];out.create_dataset('motifs/'+row['id'],data=q['fragment'][:])
                for slot in range(4):
                    entry=make_entry(row,q,slot,len(c['entries']),arm='oracle_repaint');c['entries'].append(entry);out.create_dataset(entry['dataset'],data=gen['new/'+row['id']+'/backbone'][slot][None])
        c.update(predictions=str(inputs),predictions_sha256=sha(inputs));cached=audit_refold(c,audited_generation=cached)
        with path.open('x') as f:json.dump(c,f,indent=2)
        print(partition,len(c['entries']),flush=True)


if __name__=='__main__':main()
