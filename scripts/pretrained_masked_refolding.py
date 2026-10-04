"""Gate and export all pretrained-repair outputs for matched refolding."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_fragment_preference_refold import TEACHER_KEYS,make_entry
from pretrained_masked_training_core import audit as audit_training
from prepare_overfit import sha


def require_quality(d):
    if d.get('status')!='complete' or d.get('profile_only') or not d.get('pretrained_masked') or not d.get('numerically_qualified'):raise ValueError('Completed audited full pretrained repair required')
    rows={r['arm']:r for r in d['summary']}
    if set(rows)!={'parent','native_direct','generated_cond','generated_null','native_cond','native_null'} or any(r['samples']!=128 for r in rows.values()):raise ValueError('Changed full capacity denominator')
    checks=dict(native_capacity=rows['native_cond']['raw']>=103,native_validity=rows['native_cond']['valid']>=126,generated_validity=rows['generated_cond']['valid']>=126,raw_gain_over_parent=rows['generated_cond']['raw']>rows['parent']['raw'],raw_gain_over_null=rows['generated_cond']['raw']>rows['generated_null']['raw'],families=d['refold_gate']['improved_families']>=2)
    if (rows['parent']['raw']!=25 or rows['parent']['valid']!=128 or d['refold_gate']['checks']!=checks
        or not all(checks.values()) or not d['refold_gate']['qualified'] or not d['qualified']):raise ValueError('Predeclared repair capacity/geometry gate failed')



def require_clock_quality(d,spec):
    from scaffold_clock_training_core import quality_gate
    if (d.get('status')!='complete' or d.get('profile_only') or not d.get('scaffold_clock')
            or d.get('pretrained_masked') or not d.get('numerically_qualified') or d.get('updates')!=spec['updates']):
        raise ValueError('Completed audited full scaffold-clock experiment required')
    ids=sorted({r['target_id'] for r in d['records']})
    gate=quality_gate(d['summary'],d['records'],ids,spec)
    if not gate['qualified'] or gate!=d.get('refold_gate') or not d.get('qualified'):
        raise ValueError('Predeclared whole-chain capacity/geometry gate failed')


def require_decoder_quality(d,spec,*,study='fragment_decoder'):
    from fragment_decoder_training_core import refold_eligibility
    if study=='fragment_inpainting':
        if d.get('junction_weighted'):
            raise ValueError('Junction-weighted endpoints require their separate connected-refold assay')
        from fragment_inpainting_core import refold_eligibility
    if (d.get('status')!='complete' or d.get('profile_only') or not d.get(study)
            or any(d.get(other) for other in ('pretrained_masked','scaffold_clock','fragment_decoder','fragment_decoder_fm','fragment_inpainting') if other!=study)
            or study not in ('fragment_decoder','fragment_decoder_fm','fragment_inpainting') or not d.get('numerically_qualified') or d.get('updates')!=spec['updates']):
        raise ValueError('Completed audited full fragment-decoder experiment required')
    ids=sorted({r['target_id'] for r in d['records']})
    gate=refold_eligibility(d['summary'],d['records'],ids,spec)
    if not gate['qualified'] or gate!=d.get('refold_eligibility') or not d.get('qualified'):
        raise ValueError('Fragment decoder cannot meet declared same-refold counts')


def refold_arms(study):
    return ('generated_cond','generated_untrained') if study=='fragment_inpainting' else ('generated_cond','generated_null')


def study_of(c):
    studies=[s for s in ('pretrained_masked','scaffold_clock','fragment_decoder','fragment_decoder_fm','fragment_inpainting') if c.get(s+'_refold') is True]
    if len(studies)!=1:raise ValueError('Exactly one bound repair study required')
    return studies[0]


def qualify_training(gc,d,study,*,audit_sources=True):
    if study=='fragment_inpainting':
        from fragment_inpainting_core import audit as audit_inpainting
        if audit_sources:audit_inpainting(gc)
        require_decoder_quality(d,gc['spec'],study=study)
    elif study=='fragment_decoder_fm':
        from fragment_decoder_fm_core import audit as audit_decoder_fm
        if audit_sources:audit_decoder_fm(gc)
        require_decoder_quality(d,gc['spec'],study=study)
    elif study=='fragment_decoder':
        from fragment_decoder_training_core import audit as audit_decoder
        if audit_sources:audit_decoder(gc)
        require_decoder_quality(d,gc['spec'])
    elif study=='scaffold_clock':
        from scaffold_clock_training_core import audit as audit_clock
        if audit_sources:audit_clock(gc)
        require_clock_quality(d,gc['spec'])
    elif study=='pretrained_masked':
        if audit_sources:audit_training(gc)
        require_quality(d)
    else:raise ValueError('Unknown repair study')


def audit_refold(c,*,audited_generation=None):
    from prepare_fragment_preference_refold import audit_inputs
    study=study_of(c)
    for key in ('generation_manifest','generation_report','generated_predictions','predictions','protocol','baseline_refold_manifest','baseline_refold_report'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed masked-refold input: '+key)
    gm=json.loads(Path(c['generation_manifest']).read_text());gc=gm['config'];d=json.loads(Path(c['generation_report']).read_text());spec=gc['spec'];qualify_training(gc,d,study,audit_sources=audited_generation is None)
    bm=json.loads(Path(c['baseline_refold_manifest']).read_text());bd=json.loads(Path(c['baseline_refold_report']).read_text());bc=bm['config']
    if audited_generation is None:
        original,unused=audit_inputs(bc)
    else:
        original=json.loads(Path(bc['generation_manifest']).read_text())['config']
    result=dict(gc,arm=c['arm'],prediction_group=c['arm'],native_sources=original['native_sources']);result[study+'_refold']=True
    if audited_generation is not None and audited_generation!=(result,spec):raise ValueError('Changed previously audited masked generation')
    if (gm['status']!='complete' or gm['config']['profile_only'] or d['manifest_sha256']!=c['generation_manifest_sha256'] or d['predictions_sha256']!=c['generated_predictions_sha256'] or gm['predictions_sha256']!=c['generated_predictions_sha256']
        or d['protocol_sha256']!=c['protocol_sha256'] or c['protocol']!=gc['protocol'] or d['controls']!=(192 if study in ('fragment_decoder','fragment_decoder_fm','fragment_inpainting') else 128)
        or bm['status']!='complete' or bd['status']!='complete' or bd['manifest_sha256']!=c['baseline_refold_manifest_sha256'] or bd['completed_refolds']!=256
        or bc['generation_manifest']!=gc['baseline_manifest'] or bc['generated_predictions']!=gc['baseline_predictions']
        or original['arm']!='parent6000' or original['selected']!=gc['selected'] or c['assay']!='fragment_preference_refold'
        or c['arm'] not in refold_arms(study) or c['partition'] not in range(4)
        or c['expected_backbones']!=32 or len(c['entries'])!=32 or c['allocation_minutes']!=35 or c['work_cap_seconds']!=2010
        or c.get('teacher_deterministic_algorithms') is not True or not bm['teacher_deterministic_algorithms'] or c.get('mpnn_mode','ca')!='ca'
        or any(c[k]!=bc[k] for k in TEACHER_KEYS)):raise ValueError('Changed matched pretrained refolding recipe')
    rows=[r for r in gc['selected'] if r['partition']==c['partition']]
    with h5py.File(gc['fragments']) as fr,h5py.File(c['predictions']) as out,h5py.File(c['generated_predictions']) as gen:
        wanted=[]
        for row in rows:
            q=fr['train/'+row['id']+'/conditions/c20_center']
            for slot in range(4):wanted.append(make_entry(row,q,slot,len(wanted),arm=c['arm']))
        if c['entries']!=wanted or set(out)!={'motifs'}|{r['dataset'] for r in wanted} or set(out['motifs'])!={r['id'] for r in rows}:raise ValueError('Filtered or changed repaired denominator')
        for r in wanted:
            q=fr['train/'+r['target_id']+'/conditions/c20_center']
            if not np.array_equal(out[r['dataset']][:],gen[c['arm']+'/'+r['target_id']+'/backbone'][r['generation_slot']][None]) or not np.array_equal(out['motifs/'+r['target_id']][:],q['fragment'][:]):raise ValueError('Changed repaired or supplied coordinates')
    return result,spec


def main():
    p=argparse.ArgumentParser();p.add_argument('--study',choices=('pretrained_masked','scaffold_clock','fragment_decoder','fragment_decoder_fm','fragment_inpainting'),default='pretrained_masked');p.add_argument('--generation',type=Path,required=True);p.add_argument('--baseline-run',type=Path,required=True);p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];run=a.generation.resolve();base=a.baseline_run.resolve()
    gm=json.loads((run/'manifest.json').read_text());gc=gm['config'];report=root/'reports'/(run.name+'.json');qualify_training(gc,json.loads(report.read_text()),a.study);prior=json.loads((base/'manifest.json').read_text())['config']
    for arm in refold_arms(a.study):
        cached=None
        for partition in range(4):
            path=Path(str(a.output_prefix)+f'_{arm}_{partition}.json').resolve();inputs=path.with_suffix('.h5');c={k:prior[k] for k in TEACHER_KEYS}
            c[a.study+'_refold']=True
            c.update(assay='fragment_preference_refold',arm=arm,partition=partition,expected_backbones=32,entries=[],allocation_minutes=35,work_cap_seconds=2010,teacher_deterministic_algorithms=True)
            for key,value in [('generation_manifest',run/'manifest.json'),('generation_report',report),('generated_predictions',run/'predictions.h5'),('protocol',gc['protocol']),('baseline_refold_manifest',base/'manifest.json'),('baseline_refold_report',root/'reports'/(base.name+'.json'))]:c[key]=str(value);c[key+'_sha256']=sha(value)
            with h5py.File(gc['fragments']) as fr,h5py.File(run/'predictions.h5') as gen,h5py.File(inputs,'x') as out:
                for row in (r for r in gc['selected'] if r['partition']==partition):
                    q=fr['train/'+row['id']+'/conditions/c20_center'];out.create_dataset('motifs/'+row['id'],data=q['fragment'][:])
                    for slot in range(4):
                        entry=make_entry(row,q,slot,len(c['entries']),arm=arm);c['entries'].append(entry);out.create_dataset(entry['dataset'],data=gen[arm+'/'+row['id']+'/backbone'][slot][None])
            c.update(predictions=str(inputs),predictions_sha256=sha(inputs));cached=audit_refold(c,audited_generation=cached)
            with path.open('x') as f:json.dump(c,f,indent=2)
            print(arm,partition,len(c['entries']),flush=True)


if __name__=='__main__':main()
